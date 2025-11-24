import os
import sys
from dotenv import load_dotenv
from google import genai

# Add qGen-new directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'qGen-new'))

def debug_models():
    # Load env
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dotenv_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path)

    model2 = os.getenv("MODEL2")
    print(f"Current MODEL2 in .env: {model2}")

    # Find all API keys
    api_keys = {}
    for key, value in os.environ.items():
        if key.startswith("API_") and key[4:].isdigit():
            api_keys[int(key[4:])] = value

    print(f"Found {len(api_keys)} API keys.")

    # Get thinking models list first using API_0 (assuming it can list models even if quota exceeded for generation)
    client0 = genai.Client(api_key=api_keys[0])
    thinking_models = []
    try:
        for m in client0.models.list():
            if "thinking" in m.name.lower():
                thinking_models.append(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")
        return

    print(f"Found {len(thinking_models)} thinking models: {thinking_models}")

    working_model = None
    working_key_index = None

    for index, key in sorted(api_keys.items()):
        print(f"\nChecking API_{index}...")
        client = genai.Client(api_key=key)
        
        for model in thinking_models:
            print(f"  Testing {model}...", end=" ", flush=True)
            try:
                response = client.models.generate_content(
                    model=model,
                    contents="Hi"
                )
                print("✅ OK")
                working_model = model
                working_key_index = index
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print("❌ Quota Exceeded")
                else:
                    print(f"❌ Error: {e}")
        
        if working_model:
            break

    if working_model:
        print(f"\n🎉 Found working model: {working_model} on API_{working_key_index}")
        print(f"Recommendation: Set MODEL2={working_model} in your .env file")
        print(f"Note: You might need to prioritize API_{working_key_index} in your usage.")
    else:
        print("\n⚠️ No working thinking model found on ANY key. You must wait or use a non-thinking model.")

if __name__ == "__main__":
    debug_models()
