import pickle

import os
from prisma import Prisma
from new_db import DB

def main():
    try:
        # Get the most recent pickle file from __generatedContent directory
        generated_dir = os.path.join(os.path.dirname(__file__), "__generatedContent")
        if not os.path.exists(generated_dir):
            raise FileNotFoundError("No generated content directory found")
            
        pickle_files = [f for f in os.listdir(generated_dir) if f.endswith('.pkl')]
        if not pickle_files:
            raise FileNotFoundError("No pickle files found in generated content directory")
            
        latest_file = max(pickle_files, key=lambda x: os.path.getctime(os.path.join(generated_dir, x)))
        pickle_path = os.path.join(generated_dir, latest_file)

        # Load questions from pickle file
        with open(pickle_path, "rb") as f:
            questions = pickle.load(f)
        
        print(f"✓ Successfully loaded questions from {pickle_path}")
        print(f"Found {sum(len(q) if isinstance(q, list) else 1 for q in questions.values())} questions across {len(questions)} sections")
        
        # Initialize database connection
        db = Prisma(auto_register=True)
        db.connect()
        database = DB(db)
        
        print("\nRegistering questions in database...")
        for exam_section, questions in questions.items():
            if not database.registerQuestion(exam_section, questions):
                raise Exception(f"Error registering questions for {exam_section}")
            else:
                print(f"✓ Successfully registered questions for {exam_section}")

    except FileNotFoundError as e:
        print(f"File error: {str(e)}")
        print("Please ensure questions have been generated before running this script")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        if 'db' in locals():
            db.disconnect()

if __name__ == "__main__":
    main()