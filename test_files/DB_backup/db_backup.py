import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

# Load database credentials from .env
# find_dotenv() will look for the .env file in parent directories
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
    print(f"Loaded environment variables from: {dotenv_path}")
else:
    print("Warning: .env file not found. Falling back to environment variables.")

DB_NAME = os.getenv('DATABASE_NAME', 'compex')
DB_USER = os.getenv('POSTGRES_USER', 'compexe_admin')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'QuiZA.0310!')
CONTAINER_NAME = "my-postgres"

# Setup backup directory and filename
BACKUP_DIR = os.path.dirname(os.path.abspath(__file__))
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
BACKUP_FILE = os.path.join(BACKUP_DIR, f"{DB_NAME}_backup_{TIMESTAMP}.sql")

def take_backup():
    print(f"Starting backup of database '{DB_NAME}' from container '{CONTAINER_NAME}'...")
    
    # Command to run pg_dump inside the docker container
    # We pass PGPASSWORD via -e environment variable to the container shell environment
    cmd = [
        "docker", "exec",
        "-e", f"PGPASSWORD={DB_PASS}",
        CONTAINER_NAME,
        "pg_dump",
        "-U", DB_USER,
        DB_NAME
    ]
    
    try:
        # We redirect stdout to the backup file
        with open(BACKUP_FILE, "wb") as f:
            process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                print(f"✅ Backup successful!")
                print(f"Backup file: {BACKUP_FILE}")
                print(f"File size: {os.path.getsize(BACKUP_FILE)} bytes")
            else:
                print(f"❌ Backup failed with return code {process.returncode}")
                # stderr might contain helpful error message
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                print(f"Error: {error_msg}")
                # If backup failed, the file might contain partial output or be empty
                if os.path.exists(BACKUP_FILE) and os.path.getsize(BACKUP_FILE) == 0:
                    os.remove(BACKUP_FILE)
                    
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        if os.path.exists(BACKUP_FILE):
             # Clean up if file was created but error occurred
             if os.path.getsize(BACKUP_FILE) == 0:
                os.remove(BACKUP_FILE)

if __name__ == "__main__":
    take_backup()
