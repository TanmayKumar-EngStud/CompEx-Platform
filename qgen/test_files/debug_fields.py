
from prisma import Prisma
import inspect

def main():
    db = Prisma()
    db.connect()
    
    print("--- Problems Model Fields ---")
    try:
        from prisma.models import problems
        print("Fields in 'problems' model:")
        # Try different ways to get fields
        if hasattr(problems, '__fields__'):
            print(list(problems.__fields__.keys()))
        elif hasattr(problems, 'model_fields'):
             print(list(problems.model_fields.keys()))
        else:
            print("Could not find __fields__ or model_fields.")
            print(dir(problems))
            
    except Exception as e:
        print(f"Could not inspect model directly: {e}")

    db.disconnect()

if __name__ == "__main__":
    main()
