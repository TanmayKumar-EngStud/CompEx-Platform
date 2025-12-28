import sys
import re
import os
import json
from contextlib import contextmanager
from io_utils import prettify

from db import DB
from prisma import Prisma
import time

# Singleton Prisma Client
_prisma_client = None

def get_prisma_client():
    global _prisma_client
    if _prisma_client is None:
        t0 = time.time()
        print(f"{prettify('DB', 'Yellow')}: Instantiating Prisma Client object...")
        
        # AUTO-FIX: Detect and fix host.docker.internal on local execution
        # This prevents the 5-10s DNS timeout on Mac/Linux hosts
        current_url = os.environ.get('DATABASE_URL', '')
        if 'host.docker.internal' in current_url:
            print(f"{prettify('DB Fix', 'Magenta')}: Detected 'host.docker.internal' while running locally.")
            print(f"{prettify('DB Fix', 'Magenta')}: Auto-switching to '127.0.0.1' for speed...")
            os.environ['DATABASE_URL'] = current_url.replace('host.docker.internal', '127.0.0.1')
            
        _prisma_client = Prisma()
        print(f"{prettify('DB', 'Green')}: Client instantiated in {time.time() - t0:.4f}s")
    
    if not _prisma_client.is_connected():
        # Log which URL we are trying to connect to (Mask password)
        url = os.environ.get('DATABASE_URL', 'Not Set')
        masked_url = re.sub(r':([^@]+)@', ':****@', url) if url else "None"
        
        print(f"{prettify('DB', 'Yellow')}: Connecting to database engine at {masked_url}...")
        t1 = time.time()
        try:
            _prisma_client.connect()
            elapsed = time.time() - t1
            print(f"{prettify('DB', 'Green')}: Engine connected in {elapsed:.4f}s")
        except Exception as e:
            print(f"{prettify('DB Error', 'Red')}: Connection failed: {e}")
            raise e
            
    return _prisma_client

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
    # Use Singleton
    try:
        prisma = get_prisma_client()
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
    # Do not disconnect singleton client
    # finally:
    #     if prisma.is_connected():
    #         prisma.disconnect()

def get_next_generation_params():
    """
    Fetches the last analytics record to determine the next difficulty and mock status.
    Returns: (difficulty: int, is_mock: bool)
    """
    print("Fetching last run analytics...")
    
    try:
        prisma = get_prisma_client()
        # Fetch last record
        last_record = prisma.analytics.find_first(order={'created_at': 'desc'})
        
        if last_record:
            # Logic: difficulty % 5 + 1
            new_difficulty = (last_record.difficulty_level % 5) + 1
            new_is_mock = not last_record.is_mock
        else:
            # Default
            new_difficulty = 1
            new_is_mock = False
            
        return new_difficulty, new_is_mock
        
    except Exception as e:
        print(f"Analytics Fetch Error: {e}")
        return 1, False # Fallback
    # Do not disconnect singleton

def save_analytics_record(stats: dict, difficulty: int, is_mock: bool):
    """
    Saves the run statistics to the analytics table.
    """
    print("Saving Analytics...")
    try:
        prisma = get_prisma_client()
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
