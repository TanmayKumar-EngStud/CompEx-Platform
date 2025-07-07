#!/usr/bin/env python3
"""
Test script to verify generator integration with new template system.
"""

import os
import sys
from unittest.mock import Mock

# Add the project root to path and change to project root directory if in testing dir
sys.path.append('..')
if os.path.basename(os.getcwd()) == 'testing':
    os.chdir('..')

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType

def test_generator_instruction_loading():
    """Test that generators can load optimized instructions."""
    try:
        # Mock the necessary components to avoid API calls
        mock_llm = Mock()
        mock_global_state = Mock()
        mock_lock = Mock()
        
        # Test GMAT Data Sufficiency generator
        print("=== Testing GMAT Data Sufficiency Generator ===")
        from GMAT.Quants.files.dataSufficiencyQuestionGeneration import DataSufficiencyQuestionGeneration
        
        prompt = "Arithmetic - Logical Reasoning - difficulty_level: 4"
        ds_generator = DataSufficiencyQuestionGeneration(
            global_state=mock_global_state,
            lock=mock_lock,
            api_IDX=0,
            prompt=prompt
        )
        
        # Check that instructions were loaded
        print(f"Instructions loaded: {len(ds_generator.system_instructions)} characters")
        
        # Verify optimized features are present
        optimized_features = [
            "HIGH DIFFICULTY EMPHASIS",
            "DATA SUFFICIENCY FOCUS", 
            "GMAT BUSINESS CONTEXT",
            "Universal Question Generation Philosophy"
        ]
        
        for feature in optimized_features:
            if feature in ds_generator.system_instructions:
                print(f"✓ {feature} found in instructions")
            else:
                print(f"✗ {feature} NOT found in instructions")
        
        # Test GRE generator
        print("\n=== Testing GRE Problem Solving Generator ===")
        from GRE.Quants.files.simpleQuestionGeneration import SimpleQuestionGeneration
        
        prompt = "Geometry - Data Interpretation - pie chart - difficulty_level: 2"
        ps_generator = SimpleQuestionGeneration(
            global_state=mock_global_state,
            lock=mock_lock,
            api_IDX=0,
            prompt=prompt
        )
        
        print(f"Instructions loaded: {len(ps_generator.system_instructions)} characters")
        
        # Verify GRE-specific optimized features
        gre_features = [
            "FUNDAMENTAL LEVEL EMPHASIS",
            "VISUAL DATA EMPHASIS",
            "GRE ACADEMIC CONTEXT",
            "Universal Question Generation Philosophy"
        ]
        
        for feature in gre_features:
            if feature in ps_generator.system_instructions:
                print(f"✓ {feature} found in instructions")
            else:
                print(f"✗ {feature} NOT found in instructions")
        
        # Test instruction mode extraction
        print("\n=== Testing Individual Mode Instructions ===")
        question_text_instruction = ds_generator.get_instruction_for_mode("questionText")
        print(f"QuestionText mode instruction: {len(question_text_instruction)} characters")
        
        question_title_instruction = ds_generator.get_instruction_for_mode("questionTitle")
        print(f"QuestionTitle mode instruction: {len(question_title_instruction)} characters")
        
        print("\nGenerator integration test completed successfully!")
        
    except Exception as e:
        print(f"Error during generator integration test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set a dummy API key to avoid errors
    os.environ["API_0"] = "dummy_key_for_testing"
    test_generator_instruction_loading()