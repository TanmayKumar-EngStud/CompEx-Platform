
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load env from .env file
load_dotenv()

API_KEY = os.getenv("Deepseek_API_KEY")
MODEL_QUANTS = os.getenv("MODEL_Quants", "deepseek-reasoner") # deepseek-reasoner
MODEL_VERBAL = os.getenv("MODEL_Verbal", "deepseek-chat") # deepseek-chat

print(f"API Key found: {bool(API_KEY)}")
print(f"Model Quants: {MODEL_QUANTS}")
print(f"Model Verbal: {MODEL_VERBAL}")

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

def test_generation(model, temperature, system_prompt, user_prompt, use_json=False):
    print(f"\n--- Testing Model: {model} (Temp: {temperature}) ---")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        if use_json:
             kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        
        content = response.choices[0].message.content
        print("Response:")
        print(content)
        
        if use_json:
            try:
                json_content = json.loads(content)
                print("✅ Valid JSON parsed.")
                return messages + [{"role": "assistant", "content": content}]
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON.")
                return messages
        return messages + [{"role": "assistant", "content": content}]

    except Exception as e:
        print(f"❌ Error: {e}")
        return messages

# 1. Test Quants (Math, Temp 0.0) - Reasoning model
# Note: deepseek-reasoner might not support response_format='json_object' or system prompt behavior might differ.
# Let's test standard chat first for Quants if reasoner is strict.
# Actually, DeepSeek-R1 (reasoner) supports CoT.
# Let's try standard JSON request.
history = test_generation(
    MODEL_QUANTS, 
    0.0, 
    "You are a helpful assistant. Output JSON.", 
    "Give me a math problem: Solve 2x + 3 = 7. Output in JSON format: {'question': ..., 'answer': ...}",
    use_json=True
)

# 2. Multi-turn test (Verbal, Temp 1.5)
history_verbal = test_generation(
    MODEL_VERBAL, 
    1.5, 
    "You are a creative writer. Output in JSON.", 
    "Write a short poem about coding. JSON format: {'poem': ...}",
    use_json=True
)

# 3. Follow-up usage
if history_verbal:
    print("\n--- Testing Follow-up ---")
    history_verbal.append({"role": "user", "content": "Now critique the poem in JSON: {'critique': ...}"})
    
    try:
        response = client.chat.completions.create(
            model=MODEL_VERBAL,
            messages=history_verbal,
            temperature=1.5,
            response_format={"type": "json_object"}
        )
        print("Follow-up Response:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Follow-up Error: {e}")
