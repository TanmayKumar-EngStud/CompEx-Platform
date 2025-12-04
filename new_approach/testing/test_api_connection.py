import os
import sys
import unittest
from dotenv import load_dotenv
from google import genai

# Add qGen-new directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'qGen-new'))

from api_utils import GeminiGenerator

class TestAPIConnection(unittest.TestCase):
    def setUp(self):
        # Load environment variables
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        dotenv_path = os.path.join(project_root, '.env')
        load_dotenv(dotenv_path)
        
        # Find all API keys
        self.api_keys = {}
        for key, value in os.environ.items():
            if key.startswith("API_") and key[4:].isdigit():
                self.api_keys[int(key[4:])] = value

    def test_all_api_keys(self):
        """Test connection for all found API keys."""
        if not self.api_keys:
            self.fail("No API keys found in .env file (looking for API_0, API_1, etc.)")

        print(f"\nFound {len(self.api_keys)} API keys. Testing connections...")
        
        for index, key in self.api_keys.items():
            with self.subTest(api_key_index=index):
                print(f"Testing API_{index}...")
                try:
                    # Initialize generator with specific index
                    generator = GeminiGenerator(api_key_index=index, question_type="Data Sufficiency")
                    
                    # Find a valid model to use, prioritizing flash
                    valid_model = None
                    try:
                        models_list = list(generator.client.models.list())
                        # First try to find a flash model
                        for m in models_list:
                            if "flash" in m.name and "1.5" in m.name:
                                valid_model = m.name
                                break
                        # If not found, try any gemini model
                        if not valid_model:
                            for m in models_list:
                                if m.name.startswith("models/gemini"):
                                    valid_model = m.name
                                    break
                    except:
                        pass
                    
                    if not valid_model:
                        valid_model = "gemini-1.5-flash" # Fallback
                    
                    # Do not strip 'models/' prefix as it might be required
                    # if valid_model.startswith("models/"):
                    #    valid_model = valid_model[7:]

                    print(f"   Using model for test: {valid_model}")
                    response = generator.client.models.generate_content(
                        model=valid_model,
                        contents="Reply with 'OK' if you receive this."
                    )
                    
                    self.assertIsNotNone(response)
                    print(f"✅ API_{index} is working. Response: {response.text.strip() if response.text else 'Empty'}")
                    
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                        print(f"⚠️ API_{index} connected but Quota Exceeded (429). Connection is valid.")
                    else:
                        print(f"❌ API_{index} failed with error: {error_str}")
                        self.fail(f"❌ API_{index} failed: {error_str}")

def test_single_key(index: int):
    """Test a specific API key with a custom prompt."""
    print(f"\n🧪 Testing specific API Key: API_{index}")
    
    # Load env vars if not already loaded (though module level load might have happened, good to be safe)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dotenv_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path)
    
    api_key = os.getenv(f"API_{index}")
    if not api_key:
        print(f"❌ API_{index} not found in .env file.")
        return

    try:
        # Initialize generator
        generator = GeminiGenerator(api_key_index=index, question_type="Data Sufficiency")
        
        # Find a valid model (reuse logic or just default)
        valid_model = "gemini-2.5-flash"
        try:
            models_list = list(generator.client.models.list())
            for m in models_list:
                if "flash" in m.name and "2.5" in m.name:
                    valid_model = m.name
                    break
        except:
            pass
            
        print(f"   Using model: {valid_model}")
        print("   Sending prompt: 'Hello Gemini, how are you doing?'")
        
        response = generator.client.models.generate_content(
            model=valid_model,
            contents="Hello Gemini, how are you doing?"
        )
        
        if response and response.text:
            print(f"\n✅ Response received:\n{response.text.strip()}")
        else:
            print("\n⚠️  Empty response received.")
            
    except Exception as e:
        print(f"\n❌ Error testing API_{index}: {e}")



key_index = int(9)
test_single_key(key_index)
