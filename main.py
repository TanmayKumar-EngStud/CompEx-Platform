from datetime import datetime
from prisma import Prisma
import json
from GMAT.Integrated_Reasoning.IR import GMAT_IR
from GMAT.Quants.Quants import GMAT_Q
from GMAT.Verbal.Verbal import GMAT_V
from GRE.Quants.Quants import GRE_Q
from GRE.Verbal.Verbal import GRE_V
from typing import List, Dict, Any

# Initialize Prisma client
db = Prisma(auto_register=True)

def initialize_primary_tables():
    with open('PrimaryTablesDefinitions.json', 'r') as f:
        definitions = json.load(f)

    for exam_name, exam_data in definitions['examtypes'].items():
        # Check if exam type exists
        existing_exam = db.examtypes.find_first(
            where={'examtypeid': exam_data['id']}
        )
        if not existing_exam:
            exam_type = db.examtypes.create({
                'examtypeid': exam_data['id'],
                'name': exam_name,
                'description': exam_data['description']
            })
            print(f"Exam type {exam_name} created successfully")
            for section_name, section_data in exam_data['sections'].items():
                section = db.sections.create({
                    'sectionid': section_data['id'],
                    'examtypeid': exam_type.examtypeid,
                    'name': section_name,
                    'description': section_data['description']
                })

def setPrimaryUser():
    existing_user = db.users.find_first()
    if not existing_user:
        db.users.create({
            'userid': 1,
            'username': 'admin',
            'password': 'admin',
            'email': 'admin@compex.com',
            'registrationdate': datetime.now()
        })
        print("Primary user created successfully")
    else:
        print("Primary user already exists")

class QuestionGenerator:
    def __init__(self):
        self.GMAT_IR = GMAT_IR()
        self.GMAT_Q = GMAT_Q()
        self.GMAT_V = GMAT_V()
        self.GRE_Q = GRE_Q()
        self.GRE_V = GRE_V()
        
    def generate_question_with_retry(self, generator) -> Dict[str, Any]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if isinstance(generator, (GMAT_IR, GMAT_Q, GMAT_V, GRE_Q, GRE_V)):
                    return generator.generate_questions()
                else:
                    raise ValueError(f"Unsupported generator type: {type(generator)}")
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to generate question after {max_retries} attempts: {str(e)}")
                    return {"error": str(e)}
                print(f"Attempt {attempt + 1} failed, retrying...")
                continue
        return {"error": "Max retries exceeded"}
    
    def generate_questions(self) -> Dict[str, List[Dict[str, Any]]]:
        results = {
            "GMAT_IR": self.generate_question_with_retry(self.GMAT_IR),
            "GMAT_Q": self.generate_question_with_retry(self.GMAT_Q),
            "GMAT_V": self.generate_question_with_retry(self.GMAT_V),
            "GRE_Q": self.generate_question_with_retry(self.GRE_Q),
            "GRE_V": self.generate_question_with_retry(self.GRE_V),
        }
        return results

def main():
    generator = QuestionGenerator()
    results = generator.generate_questions()
    print("Question generation completed")
    return results

if __name__ == "__main__":
    db.connect()
    print(f"DB connected: {db.is_connected()}")
    try:
        initialize_primary_tables()
        setPrimaryUser()
        questions = main()
        print(f"Here are the list of questions that are generated: \n {questions}")
    finally:
        db.disconnect()
        print(f"DB connected after disconnect: {db.is_connected()}")