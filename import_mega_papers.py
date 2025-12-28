import os
import json
import re
from db_integration import save_paper_to_db

MEGA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_json_files', 'paper', 'mega_papers')

def process_files():
    print(f"Scanning {MEGA_DIR}...")
    if not os.path.exists(MEGA_DIR):
        print(f"Directory not found: {MEGA_DIR}")
        return

    files = sorted([f for f in os.listdir(MEGA_DIR) if f.endswith('.json')])
    print(f"Found {len(files)} files.")

    for filename in files:
        path = os.path.join(MEGA_DIR, filename)
        
        # Regex to extract Exam and Set Index
        # Expects: GRE_1.json, GMAT_2.json, etc.
        match = re.match(r'(GRE|GMAT)_(\d+)\.json', filename)
        
        if not match:
            print(f"Skipping {filename}: Does not match pattern.")
            continue
            
        exam_name = match.group(1)
        set_index = int(match.group(2))
        
        # Metadata Logic
        # Set 1: Diff 1, Mock False
        # Set 2: Diff 2, Mock True
        difficulty = (set_index - 1) % 5 + 1
        is_mock = (set_index % 2 == 0)
        
        print(f"\n📄 Importing {filename}:")
        print(f"   MetaData: Set={set_index} | Difficulty={difficulty} | Mock={is_mock}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                paper_data = json.load(f)
            
            # save_paper_to_db(paper_data, is_mock, difficulty)
            save_paper_to_db(paper_data, is_mock=is_mock, difficulty=difficulty)
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

if __name__ == "__main__":
    process_files()
