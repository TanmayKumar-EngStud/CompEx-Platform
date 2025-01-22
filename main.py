import warnings
warnings.filterwarnings('ignore', message='Importing debug from langchain root module is no longer supported')

from datetime import datetime
from prisma import Prisma
import json
import pickle
import os  # Moved to top level imports
from GMAT.Integrated_Reasoning.IR import GMAT_IR
from GMAT.Quants.Quants import GMAT_Q
from GMAT.Verbal.Verbal import GMAT_V
from GRE.Quants.Quants import GRE_Q
from GRE.Verbal.Verbal import GRE_V
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
import time
from db import DB

# Define directory paths as constants
GENERATED_CONTENT_DIR = "__generatedContent"
GENERATIONS_DIR = "__generations"

def ensure_directories_exist():
    """Create necessary directories if they don't exist"""
    for directory in [GENERATED_CONTENT_DIR, GENERATIONS_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

# Update pkl_path to use the constant
pkl_path = f"{GENERATED_CONTENT_DIR}/"

class QuestionGenerator:
    def __init__(self):
        self.GMAT_IR = GMAT_IR()
        self.GMAT_Q = GMAT_Q()
        self.GMAT_V = GMAT_V()
        self.GRE_Q = GRE_Q()
        self.GRE_V = GRE_V()
        self.generators = [
            ("GMAT_IR", self.GMAT_IR),
            ("GMAT_Q", self.GMAT_Q),
            ("GMAT_V", self.GMAT_V),
            ("GRE_Q", self.GRE_Q),
            ("GRE_V", self.GRE_V)
        ]
        self.retry_counts = {name: 0 for name, _ in self.generators}
        self.max_retries = 3

    def generate_question_with_retry(self, generator_tuple) -> Tuple[str, Dict[str, Any]]:
        name, generator = generator_tuple
        
        while self.retry_counts[name] < self.max_retries:
            try:
                if isinstance(generator, (GMAT_IR, GMAT_Q, GMAT_V, GRE_Q, GRE_V)):
                    result = generator.generate_questions()
                    if self.retry_counts[name] > 0:
                        print(f"✓ {name}: Successfully generated after {self.retry_counts[name]} retries")
                    return (name, result)
            except Exception as e:
                self.retry_counts[name] += 1
                if self.retry_counts[name] == self.max_retries:
                    print(f"❌ {name}: Failed after {self.max_retries} attempts")
                    print(f"   Error: {str(e)}")
                    return (name, {"error": str(e)})
                print(f"⚠️  {name}: Attempt {self.retry_counts[name]} failed, retrying...")
                print(f"   Error: {str(e)}")
                continue
        return (name, {"error": f"Max retries ({self.max_retries}) exceeded"})
    
    def generate_questions(self) -> Dict[str, List[Dict[str, Any]]]:
        results = {}
        print("\nGenerating questions for each exam section:")
        print("-------------------------------------------")
        with ThreadPoolExecutor(max_workers=len(self.generators)) as executor:
            future_to_generator = {executor.submit(self.generate_question_with_retry, gen): gen[0] for gen in self.generators}
            for future in as_completed(future_to_generator):
                name = future_to_generator[future]
                try:
                    gen_name, gen_result = future.result()
                    results[gen_name] = gen_result
                    if "error" not in gen_result:
                        print(f"✓ {name}: Successfully generated")
                except Exception as e:
                    print(f"❌ {name}: Unhandled exception: {str(e)}")
                    results[name] = {"error": str(e)}
        print("-------------------------------------------\n")
        return results

def convert_generators_to_lists(data):
    """Convert any generator objects in the data structure to lists"""
    if isinstance(data, dict):
        return {key: convert_generators_to_lists(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_generators_to_lists(item) for item in list(data)]
    elif hasattr(data, '__iter__') and not isinstance(data, (str, bytes, bytearray)):
        try:
            return list(data)
        except:
            return data
    return data

def save_questions_to_files(questions_data):
    """Save questions to files with robust error handling"""
    # Ensure directories exist before saving files
    ensure_directories_exist()
    
    # First convert any generators to lists
    questions_data = convert_generators_to_lists(questions_data)
    
    # Generate filenames with timestamp
    timestamp = datetime.now().strftime('%d-%H-%M-%S')
    file_name = f"data-{timestamp}.pkl"
    representation_file_name = f"data-{timestamp}.json"
    temp_pkl_path = os.path.join(GENERATED_CONTENT_DIR, f"{file_name}_temp.pkl")
    final_pkl_path = os.path.join(GENERATED_CONTENT_DIR, file_name)
    json_path = os.path.join(GENERATIONS_DIR, representation_file_name)

    try:
        # Save to temporary pickle file
        with open(temp_pkl_path, "wb") as f:
            pickle.dump(questions_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Verify the pickle file by loading it
        with open(temp_pkl_path, "rb") as f:
            loaded_data = pickle.load(f)
        
        # If verification successful, rename to final file
        if os.path.exists(final_pkl_path):
            backup_path = f"{final_pkl_path}.bak"
            os.rename(final_pkl_path, backup_path)
            print(f"Created backup of existing file: {backup_path}")
            
        os.rename(temp_pkl_path, final_pkl_path)
        print(f"Questions saved to {file_name} successfully")
        
        # Save as JSON for human-readable backup
        with open(json_path, "w", encoding='utf-8') as f:
            json.dump(questions_data, f, indent=2, ensure_ascii=False)
        print(f"Questions saved to {representation_file_name} successfully")
        
        # Verify the saved data matches original
        if str(loaded_data) == str(questions_data):
            print("Data verification successful - saved data matches original")
        else:
            print("Warning: Saved data verification failed - contents may not match exactly")
            
    except Exception as e:
        print(f"Error saving questions to file: {str(e)}")
        if os.path.exists(temp_pkl_path):
            os.remove(temp_pkl_path)  # Clean up temp file if it exists
        raise

def main():
    generator = QuestionGenerator()
    results = generator.generate_questions()
    print("Question generation completed")
    return results

if __name__ == "__main__":
    # Initialize single Prisma client
    db = Prisma(auto_register=True)
    db.connect()
    start_time = time.time()
    print(f"DB connected: {db.is_connected()}")
    
    try:
        # Initialize DB handler with existing Prisma client
        db_handler = DB(db)
        
        # Generate and register questions
        questions = main()
        
        # Save the questions
        save_questions_to_files(questions)
        
        print("\nGenerated questions:")
        print(json.dumps(questions, indent=2))
        
        print("\nRegistering questions in database...")
        for section, section_questions in questions.items():
            try:
                if isinstance(section_questions, dict) and "error" in section_questions:
                    print(f"❌ Skipping {section} due to generation error: {section_questions['error']}")
                    continue
                    
                print(f"Registering {section} questions...")
                if section == "GMAT_IR":
                    for question in section_questions:
                        db_handler._register_gmat_ir_question(question)
                elif section == "GMAT_Q":
                    for question in section_questions:
                        db_handler._register_gmat_quants_question(question)
                elif section == "GMAT_V":
                    db_handler._register_gmat_verbal_question(section_questions)
                elif section == "GRE_Q":
                    for question in section_questions:
                        db_handler._register_gre_quants_question(question)
                elif section == "GRE_V":
                    for question in section_questions:
                        db_handler._register_gre_verbal_question(question)
                print(f"✓ Successfully registered {section} questions")
            except Exception as e:
                print(f"❌ Error registering {section} questions: {str(e)}")
                continue
        
        print("✓ Question registration completed")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        db.disconnect()
        print(f"DB connected after disconnect: {db.is_connected()}")
        end_time = time.time()
        print(f"Total time taken: {end_time - start_time} seconds")