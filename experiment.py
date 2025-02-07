import json
import os
from prisma import Prisma
from db import DB

def main():
    try:
        # Get the most recent pickle file from __generatedContent directory
        with open(os.path.join(os.path.dirname(__file__), "GMAT_paper-06-02-2025-21-53.json"), "r") as f:
            paper = json.load(f)
        # print(f"Found {sum(len(q) if isinstance(q, list) else 1 for q in paper.values())} questions across {len(paper)} sections")
        
        # Initialize database connection
        db = Prisma(auto_register=True)
        db.connect()
        database = DB(db)
        
        print("\nRegistering questions in database...")
# 😵 comment this for loop to ignore registering questions
        database.registerQuestion(paper, isMockQuestion=True, difficulty=1)
    finally:
        if 'db' in locals():
            db.disconnect()

if __name__ == "__main__":
    main()