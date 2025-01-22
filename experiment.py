import pickle
import json
import os
from prisma import Prisma
from db import DB

def save_questions_to_files(questions_data):
    """Save questions to both pickle and JSON files with verification"""
    # First save to a temporary pickle file
    with open("data_temp.pkl", "wb") as f:
        pickle.dump(questions_data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    # Verify the saved data
    with open("data_temp.pkl", "rb") as f:
        loaded_data = pickle.load(f)
    
    # If verification successful, rename temp file
    if loaded_data == questions_data:
        # Backup existing data.pkl if it exists
        if os.path.exists("data.pkl"):
            os.rename("data.pkl", "data.pkl.bak")
        os.rename("data_temp.pkl", "data.pkl")
        
        # Also save as JSON for human-readable backup
        with open("data.json", "w") as f:
            json.dump(questions_data, f, indent=2)
        print("✓ Questions successfully saved to data.pkl and data.json")
    else:
        os.remove("data_temp.pkl")
        raise ValueError("Data verification failed - saved data does not match original")

def main():
    try:
        # Load questions from pickle file
        with open("__generatedContent/data-22-15-13-24.pkl", "rb") as f:
            questions = pickle.load(f)
        
        print("✓ Successfully loaded questions from data.pkl")
        print(f"Found {sum(len(q) if isinstance(q, list) else 1 for q in questions.values())} questions across {len(questions)} sections")
        
        # Initialize database connection
        db = Prisma(auto_register=True)
        db.connect()
        database = DB(db)
        
        print("\nRegistering questions in database...")
        database.register_questions(questions)
        print("✓ Successfully registered all questions in database")
        
        # Save questions to files (both pickle and JSON)
        save_questions_to_files(questions)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        if 'db' in locals():
            db.disconnect()


main()