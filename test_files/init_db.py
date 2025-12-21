import sys
import os

# Add parent directory to path to allow importing modules from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prisma import Prisma
from db import DB

def run_init():
    print("Starting DB Initialization...")
    prisma = Prisma()
    try:
        prisma.connect()
        print("Connected to Database.")
        
        # Instantiating DB triggers _initialize_primary_tables automatically in __init__
        db_instance = DB(prisma)
        
        print("Initialization Logic Completed.")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
    finally:
        if prisma.is_connected():
            prisma.disconnect()
            print("Disconnected from Database.")

if __name__ == "__main__":
    run_init()
