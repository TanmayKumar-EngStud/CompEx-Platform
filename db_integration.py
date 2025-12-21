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

def save_paper_to_db(paper_data, is_mock=True, difficulty=None):
    """
    Saves the full paper to the database.
    """
    if difficulty is None:
        try:
            difficulty, _ = get_next_generation_params()
        except:
            difficulty = 1 # Fallback only if everything fails
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
        success = db_instance.registerQuestion(formatted_paper, isMockQuestion=is_mock, difficulty=difficulty)
        
        if success:
            print("Successfully saved paper to database.")
        else:
            print("Failed to save some or all questions to database.")
            
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        if prisma.is_connected():
            prisma.disconnect()

def get_next_generation_params():
    """
    Fetches the last analytics record to determine the next difficulty and mock status.
    Returns: (difficulty: int, is_mock: bool)
    """
    print("Fetching last run analytics...")
    prisma = Prisma()
    try:
        prisma.connect()
        # Fetch last record
        last_record = prisma.analytics.find_first(order={'created_at': 'desc'})
        
        if last_record:
            # Logic: difficulty % 5 + 1
            new_difficulty = (last_record.difficulty_level % 5) + 1
            # Logic: flip is_mock if it was True, else ? 
            # User said: "if for the last record had is_mock = True, for this time's generation will have is_mock as false"
            # "if there is no record ... is_mock = False"
            # Wait, user logic is slightly ambiguous for the False case.
            # "if last record had is_mock = True -> this time False"
            # It implies a toggle? Or just "True -> False"? What if last was False?
            # User said: "thus storing the questions in the database as independent questions ... if the question is stored as mock paper..."
            # It sounds like a toggle: True -> False -> True? 
            # "fetching the last record ... difficulty_level%5+1; and if for the last record had is_mock = True, for this time's generation will have is_mock as false... if there is no record ... is_mock = False"
            # This implies incomplete logic in description. 
            # I will assume TOGGLE behavior: True <-> False.
            # Rationale: If last was False, next should be True?
            # Let's re-read: "if for the last record had is_mock = True, for this time's generation will have is_mock as false"
            # It doesn't explicitly say "if last was False, make it True".
            # BUT, generally these are cycles.
            # However, start state is False.
            # If start is False. Next should be True?
            # User instruction: "if there is no record in the analyitics table, then we will be having is_mock = False and difficulty_level as 1"
            # So sequence: 
            # 1. No record -> Mock=False, Diff=1.
            # 2. Next run -> Last=False. ? 
            # If logic is ONLY "if last=True then False", then False -> False forever? That breaks the "mock logic".
            # It must be a toggle.
            new_is_mock = not last_record.is_mock
        else:
            # Default
            new_difficulty = 1
            new_is_mock = False
            
        return new_difficulty, new_is_mock
        
    except Exception as e:
        print(f"Analytics Fetch Error: {e}")
        return 1, False # Fallback
    finally:
        if prisma.is_connected():
            prisma.disconnect()

def save_analytics_record(stats: dict, difficulty: int, is_mock: bool):
    """
    Saves the run statistics to the analytics table.
    """
    print("Saving Analytics...")
    prisma = Prisma()
    try:
        prisma.connect()
        # Conversion
        t_in = stats.get('total_input_tokens', 0) / 1_000_000
        t_out = stats.get('total_output_tokens', 0) / 1_000_000
        t_time = stats.get('total_time_seconds', 0.0) / 60

        prisma.analytics.create(data={
            'total_api_calls': stats.get('total_api_calls', 0),
            'total_input_tokens': f"{t_in:.3f}M",
            'total_output_tokens': f"{t_out:.3f}M",
            'total_time_minutes': float(f"{t_time:.2f}"), # Ensure float precision match
            'gre_questions': stats.get('gre_questions', 0),
            'gmat_questions': stats.get('gmat_questions', 0),
            'difficulty_level': difficulty,
            'is_mock': is_mock
        })
        print("Analytics saved successfully.")
    except Exception as e:
        print(f"Analytics Save Error: {e}")
    finally:
        if prisma.is_connected():
            prisma.disconnect()
