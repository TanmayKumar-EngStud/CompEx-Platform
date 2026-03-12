
import sys
import os
import json
import re

# Add project root to path
# Assuming this script is in test_files/store_papers/
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from db_integration import save_paper_to_db

def store_mock_papers():
    paper_dir = os.path.join(project_root, 'log_json_files', 'paper', 'mega_papers')
    
    if not os.path.exists(paper_dir):
        print(f"Directory not found: {paper_dir}")
        return

    files = sorted(os.listdir(paper_dir))
    
    # Regex to match GRE_new_{index}.json and GMAT_new_{index}.json
    pattern = re.compile(r'(GRE|GMAT)_\d+\.json')

    for filename in files:
        if pattern.match(filename):
            file_path = os.path.join(paper_dir, filename)
            print(f"Processing {filename}...")
            
            try:
                with open(file_path, 'r') as f:
                    raw_paper_data = json.load(f)
                
                # Extract exam name from filename (GRE or GMAT)
                exam_name = filename.split('_')[0]
                
                # Wrap it in the expected structure: { "GRE": { ... } }
                paper_data = { exam_name: raw_paper_data }
                
                print(f"  -> Storing as Mock Test (Difficulty=2)...")
                save_paper_to_db(paper_data, is_mock=True, difficulty=3)
                print(f"  -> Done.")
                
            except Exception as e:
                print(f"  -> Error processing {filename}: {e}")


store_mock_papers()
