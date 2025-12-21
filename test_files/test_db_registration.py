
import json
import os
import sys
from prisma import Prisma
from db import DB

# MOCK DATA PATHS
GRE_JSON_PATH = 'log_json_files/paper/GRE.json'
GMAT_JSON_PATH = 'log_json_files/paper/GMAT.json'

def transform_and_register(db_manager, data, exam_name):
    """Transform JSON data to match the expected registerQuestion format"""
    # Original format: {"key": {"section": "Verbal", "questions": [...]}}
    # Expected format: {"GRE_V": {"1": [...]}, "GRE_Q": {"1": [...]}}
    
    transformed_paper = {}
    section_map = {
        "Quants": "Q",
        "Verbal": "V",
        "Integrated Reasoning": "IR"
    }
    
    for key, content in data.items():
        if not isinstance(content, dict) or "section" not in content:
            continue
            
        json_section = content["section"]
        short_section = section_map.get(json_section)
        
        if not short_section:
            print(f"Warning: Unknown section '{json_section}' in {exam_name}")
            continue
            
        exam_section_key = f"{exam_name}_{short_section}"
        
        if exam_section_key not in transformed_paper:
            transformed_paper[exam_section_key] = {}
            
        # We can use the original key from the JSON as the sub-section number
        transformed_paper[exam_section_key][key] = content.get("questions", [])
        
    if transformed_paper:
        return db_manager.registerQuestion(transformed_paper)
    return False

def main():
    prisma = Prisma()
    prisma.connect()
    
    db_manager = DB(prisma)
    
    # Register GRE
    print(f"Loading {GRE_JSON_PATH}...")
    if os.path.exists(GRE_JSON_PATH):
        with open(GRE_JSON_PATH, 'r') as f:
            gre_data = json.load(f)
        print("Registering GRE questions...")
        success = transform_and_register(db_manager, gre_data, "GRE")
        print(f"GRE Registration success: {success}")
    else:
        print(f"Error: {GRE_JSON_PATH} not found")

    # Register GMAT
    print(f"Loading {GMAT_JSON_PATH}...")
    if os.path.exists(GMAT_JSON_PATH):
        with open(GMAT_JSON_PATH, 'r') as f:
            gmat_data = json.load(f)
        print("Registering GMAT questions...")
        success = transform_and_register(db_manager, gmat_data, "GMAT")
        print(f"GMAT Registration success: {success}")
    else:
        print(f"Error: {GMAT_JSON_PATH} not found")

    prisma.disconnect()

if __name__ == '__main__':
    main()
