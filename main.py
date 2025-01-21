import warnings
warnings.filterwarnings('ignore', message='Importing debug from langchain root module is no longer supported')

from datetime import datetime
from prisma import Prisma
import json
import pickle
from GMAT.Integrated_Reasoning.IR import GMAT_IR
from GMAT.Quants.Quants import GMAT_Q
from GMAT.Verbal.Verbal import GMAT_V
from GRE.Quants.Quants import GRE_Q
from GRE.Verbal.Verbal import GRE_V
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import time
from db import DB

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

    def generate_question_with_retry(self, generator_tuple) -> Dict[str, Any]:
        max_retries = 3
        name, generator = generator_tuple
        for attempt in range(max_retries):
            try:
                if isinstance(generator, (GMAT_IR, GMAT_Q, GMAT_V, GRE_Q, GRE_V)):
                    result = generator.generate_questions()
                    return (name, result)
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to generate question after {max_retries} attempts: {str(e)}")
                    return (name, {"error": str(e)})
                print(f"Attempt {attempt + 1} failed, retrying...")
                continue
        return (name, {"error": "Max retries exceeded"})
    
    def generate_questions(self) -> Dict[str, List[Dict[str, Any]]]:
        results = {}
        with ThreadPoolExecutor(max_workers=len(self.generators)) as executor:
            future_to_generator = {executor.submit(self.generate_question_with_retry, gen): gen[0] for gen in self.generators}
            for future in as_completed(future_to_generator):
                name = future_to_generator[future]
                try:
                    gen_name, gen_result = future.result()
                    results[gen_name] = gen_result
                except Exception as e:
                    print(f"Unhandled exception for {name}: {str(e)}")
                    results[name] = {"error": str(e)}
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
        print(f"questions generated \n {questions}\n\n")
        
        # Save generated questions to files with robust error handling
        def save_questions_to_files(questions_data):
            import os  # Import at the start of the function
            
            # First convert any generators to lists
            questions_data = convert_generators_to_lists(questions_data)
            
            # First save to a temporary pickle file
            temp_pkl_path = "data_temp.pkl"
            try:
                with open(temp_pkl_path, "wb") as f:
                    pickle.dump(questions_data, f, protocol=pickle.HIGHEST_PROTOCOL)
                
                # Verify the pickle file by loading it
                with open(temp_pkl_path, "rb") as f:
                    loaded_data = pickle.load(f)
                
                # If verification successful, rename to final file
                if os.path.exists("data.pkl"):
                    os.rename("data.pkl", "data.pkl.bak")  # Create backup of existing file
                os.rename(temp_pkl_path, "data.pkl")
                print("Questions saved to data.pkl successfully")
                
                # Also save as JSON for human-readable backup
                with open("data.json", "w", encoding='utf-8') as f:
                    json.dump(questions_data, f, indent=2, ensure_ascii=False)
                print("Questions saved to data.json successfully")
                
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
        
        # Save the questions
        save_questions_to_files(questions)
        
        print("\nGenerated questions:")
        print(json.dumps(questions, indent=2))
        
        print("\nRegistering questions in database...")
        db_handler.register_questions(questions)
        print("Questions registered successfully")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        db.disconnect()
        print(f"DB connected after disconnect: {db.is_connected()}")
        end_time = time.time()
        print(f"Total time taken: {end_time - start_time} seconds")