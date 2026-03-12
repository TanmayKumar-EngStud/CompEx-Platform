import os
import sys
import json

# Add root directory to sys.path to allow imports from root
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from db_integration import save_paper_to_db
    from io_utils import prettify
except ImportError as e:
    print(f"Import Error: {e}")
    print("Please ensure you are running this from the project root or the test_files directory.")
    sys.exit(1)

def main():
    """
    Script to register existing GMAT.json and GRE.json files into the database.
    Settings: Difficulty Level 3, isMock = False
    """
    # 1. Paths to JSON files (relative to root)
    gre_json_path = os.path.join(root_dir, 'log_json_files', 'paper', 'GRE.json')
    gmat_json_path = os.path.join(root_dir, 'log_json_files', 'paper', 'GMAT.json')
    
    # 2. Setup papers dictionary for db_integration
    # db_integration transforms { "EXAM": { "id": { ... } } }
    papers_to_register = {}

    print(f"\n{prettify('SEARCHING FOR PAPERS', 'Cyan', True)}")

    # Load GRE
    if os.path.exists(gre_json_path):
        print(f"↳ Found GRE paper. Loading...")
        with open(gre_json_path, 'r', encoding='utf-8') as f:
            papers_to_register["GRE"] = json.load(f)
    else:
        print(f"↳ {prettify('Warning', 'Yellow')}: {gre_json_path} not found.")

    # Load GMAT
    if os.path.exists(gmat_json_path):
        print(f"↳ Found GMAT paper. Loading...")
        with open(gmat_json_path, 'r', encoding='utf-8') as f:
            papers_to_register["GMAT"] = json.load(f)
    else:
        print(f"↳ {prettify('Warning', 'Yellow')}: {gmat_json_path} not found.")

    if not papers_to_register:
        print(f"{prettify('Error', 'Red')}: No papers found to register. Exiting.")
        return

    # 3. Call registration logic
    # User Request: Difficulty Level 3, isMock = False
    print(f"\n{prettify('STARTING DB REGISTRATION', 'Green', True)}")
    print(f"↳ {prettify('Target Difficulty', 'Yellow')}: 3")
    print(f"↳ {prettify('Is Mock Paper', 'Yellow')}: False")
    
    try:
        save_paper_to_db(papers_to_register, is_mock=False, difficulty=3)
        print(f"\n{prettify('SUCCESS', 'Green', True)}: Registration process completed.")
    except Exception as e:
        print(f"\n{prettify('CRITICAL ERROR during registration', 'Red')}: {e}")

if __name__ == "__main__":
    main()
