import sys
import os

# Add parent directory to sys.path to allow importing modules from root
# This is crucial for accessing shared logic like question_manager.py
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
