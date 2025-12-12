
import os
import json
import time
from typing import Dict, Any, Optional, Union, List, Tuple
from openai import OpenAI
from dotenv import load_dotenv

from io_utils import prettify

# Load environment variables
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

import threading

# Global Singleton State
_client_instance = None
_client_lock = threading.Lock()
_model_quants = "deepseek-reasoner"
_model_verbal = "deepseek-chat"

def get_deepseek_client() -> OpenAI:
    """Thread-safe singleton accessor for OpenAI client."""
    global _client_instance, _model_quants, _model_verbal
    
    if _client_instance is None:
        with _client_lock:
            # Double-check locking
            if _client_instance is None:
                api_key = os.getenv("Deepseek_API_KEY")
                if not api_key:
                    raise ValueError("Deepseek_API_KEY invalid or missing in .env")
                
                _client_instance = OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com"
                )
                _model_quants = os.getenv("MODEL_Quants", "deepseek-reasoner")
                _model_verbal = os.getenv("MODEL_Verbal", "deepseek-chat")
                
    return _client_instance

def get_deepseek_model(question_type: str) -> Tuple[str, float]:
    """Returns (model_name, temperature) based on question type."""
    # Ensure initialized (to load env vars)
    get_deepseek_client()
    
    qt_lower = question_type.lower()
    if any(x in qt_lower for x in ["quant", "math", "data sufficiency", "problem solving", "numerical", "integrated reasoning", "table", "graph", "chart", "two-part"]):
        return _model_quants, float(os.getenv("temp_Quants", 0.0))
    else:
        return _model_verbal, float(os.getenv("temp_Verbal", 1.5))


class DeepseekSession:
    """
    Stateful session for a single question generation flow.
    Maintains conversation history (messages list).
    """
    def __init__(self, question_type: str):
        self.client = get_deepseek_client()
        self.question_type = question_type
        self.model, self.temperature = get_deepseek_model(question_type)
        self.messages = []
        self.system_instructions_set = False

    def set_system_instruction(self, instruction: str):
        """Sets the system instruction (first message)."""
        if not self.system_instructions_set:
            self.messages.insert(0, {"role": "system", "content": instruction})
            self.system_instructions_set = True

    def generate_component(self, 
                          instruction_statement: str, 
                          expected_output: Union[str, Dict], 
                          context: Optional[Dict] = None) -> Tuple[Union[str, Dict], Dict]:
        """
        Generates a component within the current conversation context.
        """
        # 1. format the user message
        component_type = context.get('component_type', 'Unknown') if context else 'Unknown'
        
        # Build prompt
        user_content = f"Instruction for {component_type}:\n{instruction_statement}"
        if context and context.get('metadata_content'):
             user_content += f"\n\nMetadata Context:\n{json.dumps(context['metadata_content'], indent=2)}"

        self.messages.append({"role": "user", "content": user_content})

        # 2. Call API
        try:
            # Check if json mode is requested (implicit if expected_output is dict or we want structured data)
            # User output instructions usually ask for JSON.
            # Deepseek supports json_object response_format.
            use_json = True 
            
            # Deepseek Reasoner (deepseek-reasoner) limitation check:
            # If using 'deepseek-reasoner', check docs or assume it behaves like R1.
            # R1 might warn on system prompt or high temp. 
            # Use beta features if needed, but 'chat.completions.create' is standard.
            
            kwargs = {
                "model": self.model,
                "messages": self.messages,
                "temperature": self.temperature,
                "stream": False
            }
            if use_json:
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content
            
            # 3. Validation & Parsing
            parsed_data = self._parse_json(content)
            
            # 4. Update History
            self.messages.append({"role": "assistant", "content": content})
            
            # 5. Stats
            stats = {
                'input_tokens': response.usage.prompt_tokens,
                'output_tokens': response.usage.completion_tokens
            }
            
            return parsed_data, stats

        except Exception as e:
            # Log error
            print(f"{prettify('Deepseek Error', 'Red')}: {e}")
            raise e

    def _parse_json(self, content: str) -> Union[Dict, str]:
        # Basic cleaning
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # If plain string was expected or fallback
            return content
