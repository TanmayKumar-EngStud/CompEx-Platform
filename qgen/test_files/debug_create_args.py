
from prisma import Prisma
import inspect
from prisma.models import problems

def main():
    print("--- problems.create Signature ---")
    sig = inspect.signature(problems.prisma().create)
    print(sig)
    
    print("\n--- problems.create parameters ---")
    for name, param in sig.parameters.items():
        print(f"{name}: {param.annotation}")
        
    print("\n--- Examining 'data' argument type if possible ---")
    # 'data' argument usually expects a TypedDict
    # But usually it's just 'data: problemsCreateInput' in comments or type hints.
    # Let's try to print annotations of the model class itself again for snake_case confirmation
    print("\n--- Model Fields (Standardized) ---")
    try:
        # Check for model_fields in pydantic models which prisma-python uses
        if hasattr(problems, 'model_fields'):
            for k, v in problems.model_fields.items():
                print(f"{k} (alias={v.alias})")
    except Exception as e:
        print(f"Error inspecting model_fields: {e}")

if __name__ == "__main__":
    main()
