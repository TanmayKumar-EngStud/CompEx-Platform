import sys
import os
import json
from contextlib import contextmanager

from db import DB
from prisma import Prisma

SECTION_MAPPING = {
    # Schema: Exam -> Section ID -> Name
    # db.py expects "EXAM_CODE" (e.g. GMAT_Q)
    # Our generated paper has: "GMAT": {"1": {"section": "Quants", ...}}
    "GMAT": {
        "Quants": "GMAT_Q",
        "Verbal": "GMAT_V",
        "Integrated Reasoning": "GMAT_IR"
    },
    "GRE": {
        "Quants": "GRE_Q",
        "Verbal": "GRE_V"
    }
}

def transform_exam_data(paper_data):
    """
    Transforms the nested dictionary from main.py genQ into the format expected by db.py.
    
    Input:
    {
       "GMAT": {
           "1": { "section": "Quants", "questions": [...] },
           "2": { "section": "Verbal", ... }
       }
    }
    
    Output:
    {
       "GMAT_Q": { "1": [...] }, # mapped section number
       "GMAT_V": { ... }
    }
    """
    transformed_paper = {}
    
    for exam_name, sections in paper_data.items():
        if exam_name not in SECTION_MAPPING:
            print(f"Skipping unknown exam: {exam_name}")
            continue
            
        for section_id_str, section_content in sections.items():
            section_name = section_content.get('section')
            questions = section_content.get('questions', [])
            
            # Find DB code (e.g. GMAT_Q)
            db_exam_code = SECTION_MAPPING[exam_name].get(section_name)
            
            if not db_exam_code:
                print(f"Warning: No mapping for section '{section_name}' in exam '{exam_name}'")
                continue
                
            # Initialize if new
            if db_exam_code not in transformed_paper:
                transformed_paper[db_exam_code] = {}
                
            # DB.registerQuestion expects { sectionNumber: [questions] }
            # We preserve the section ID (e.g. "1")
            transformed_paper[db_exam_code][section_id_str] = questions
            
    return transformed_paper

def save_paper_to_db(paper_data, is_mock=True):
    """
    Saves the full paper to the database.
    """
    if not DB or not Prisma:
        print("Database client not available. Skipping DB persistence.")
        return

    print("Initializing Database Connection...")
    prisma = Prisma()
    try:
        prisma.connect()
        db_instance = DB(prisma)
        
        # Transform data
        formatted_paper = transform_exam_data(paper_data)
        
        if not formatted_paper:
            print("No valid paper data to save.")
            return

        print(f"Persisting paper structure: {list(formatted_paper.keys())}")
        
        # Register
        # registerQuestion(paper, isMockQuestion=True, difficulty=?)
        # db.py iterates over the paper dict.
        # It handles transaction internally? No, it just loops.
        
        success = db_instance.registerQuestion(formatted_paper, isMockQuestion=is_mock, difficulty=5) # Default difficulty 5 for mock
        
        if success:
            print("Successfully saved paper to database.")
        else:
            print("Failed to save some or all questions to database.")
            
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        if prisma.is_connected():
            prisma.disconnect()
