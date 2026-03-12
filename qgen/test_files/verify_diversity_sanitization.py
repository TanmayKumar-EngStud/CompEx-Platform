import sys
import os
import random
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock modules that cause import errors because of missing dependencies
sys.modules['generator'] = MagicMock()
sys.modules['thread_creator'] = MagicMock()
sys.modules['deepseek_utils'] = MagicMock()
sys.modules['openai'] = MagicMock()

from prepare_prompts import PromptPrep
from content_generation_manager import manage_generated_content

def test_diversity_buffer():
    print("--- Testing Diversity Buffer (Simulation) ---")
    PromptPrep.topic_usage_counts = {}
    
    if hasattr(PromptPrep, 'topic_usage_counts'):
        print("✅ PromptPrep.topic_usage_counts is initialized.")
        PromptPrep.topic_usage_counts['TopicA'] = 2
        print(f"Set count for TopicA to 2")
        
        # Test the static helper method _get_buffered_choice
        options = ["TopicA", "TopicB", "TopicC"]
        
        # TopicA has 2 uses. Limit is 3. It should still be selectable.
        # Let's force it to 3
        PromptPrep.topic_usage_counts['TopicA'] = 3
        print("Set count for TopicA to 3 (Limit reached).")
        
        # Now if we select from [TopicA, TopicB], TopicA should be excluded
        filtered_options = ["TopicA", "TopicB"]
        
        print(f"Picking from {filtered_options} 100 times...")
        selections = []
        for _ in range(100):
            # We can't call _get_buffered_choice directly if it's private or if the random seed makes it hard to prove exclusion without many trials
            # But we can call the method if we access it
            choice = PromptPrep._get_buffered_choice(filtered_options, limit=3)
            selections.append(choice)
            
        if "TopicA" not in selections:
            print("✅ Verified: TopicA was excluded after reaching limit 3.")
        else:
            print(f"❌ Failed: TopicA appeared {selections.count('TopicA')} times despite limit 3.")
            
    else:
        print("❌ PromptPrep.topic_usage_counts is MISSING.")

def test_solution_sanitization():
    print("\n--- Testing Solution Sanitization ---")
    result_buffer = {}
    
    # Mock data from LLM
    start_data = {
        "scratchpad": "This is internal thought.",
        "solution": "This is the final answer."
    }
    
    try:
        manage_generated_content(result_buffer, "Problem Solving Simple", "QuestionSolution", start_data)
        
        if result_buffer.get('solution') == "This is the final answer." and 'scratchpad' not in result_buffer:
            print("✅ Sanitization Successful: Only 'solution' extracted.")
        elif 'scratchpad' in result_buffer:
             print("❌ Failed: 'scratchpad' leaked into result.")
        else:
            print(f"❌ Failed: Unexpected result: {result_buffer}")
            
    except Exception as e:
        print(f"❌ Error during sanitization test: {e}")

if __name__ == "__main__":
    test_diversity_buffer()
    test_solution_sanitization()
