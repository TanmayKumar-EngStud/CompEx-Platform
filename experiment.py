import json
import os
from prisma import Prisma
from db import DB

def main():
    try:
        # Get the most recent pickle file from __generatedContent directory
        with open(os.path.join(os.path.dirname(__file__), "__generations/data.json"), "r") as f:
            questions = json.load(f)
        print(f"Found {sum(len(q) if isinstance(q, list) else 1 for q in questions.values())} questions across {len(questions)} sections")
        
        # Initialize database connection
        db = Prisma(auto_register=True)
        db.connect()
        database = DB(db)
        
        print("\nRegistering questions in database...")
# 😵 comment this for loop to ignore registering questions
        for exam_section, questions in questions.items():
            if not database.registerQuestion(exam_section, questions):
                print(f"❌ Error registering questions for {exam_section}")
            else:
                print(f"✅ Successfully registered questions for {exam_section}")

    finally:
        if 'db' in locals():
            db.disconnect()

if __name__ == "__main__":
    main()