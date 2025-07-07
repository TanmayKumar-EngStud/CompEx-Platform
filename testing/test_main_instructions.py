#!/usr/bin/env python3
"""
Test script to verify main instruction integration.
"""

import sys
import os
# Add the project root to path and change to project root directory if in testing dir
sys.path.append('..')
if os.path.basename(os.getcwd()) == 'testing':
    os.chdir('..')

from core.instructions.instruction_manager import InstructionManager
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType

def test_main_instruction_loading():
    """Test loading of main instructions."""
    try:
        manager = InstructionManager()
        
        # Test with data sufficiency
        print("Testing GMAT Data Sufficiency Main Instruction...")
        instruction = manager.get_main_instruction(ExamType.GMAT, QuestionType.DATA_SUFFICIENCY)
        print(f"Loaded instruction length: {len(instruction)} characters")
        print(f"First 200 characters: {instruction[:200]}...")
        
        # Test with problem solving
        print("\nTesting GRE Problem Solving Main Instruction...")
        instruction = manager.get_main_instruction(ExamType.GRE, QuestionType.PROBLEM_SOLVING)
        print(f"Loaded instruction length: {len(instruction)} characters")
        print(f"First 200 characters: {instruction[:200]}...")
        
        # Test full instruction with all modes
        print("\nTesting Full Instruction (all modes) for GMAT Data Sufficiency...")
        full_instruction = manager.get_all_modes_instruction(ExamType.GMAT, QuestionType.DATA_SUFFICIENCY)
        print(f"Full instruction length: {len(full_instruction)} characters")
        
        print("\nMain instruction integration test completed successfully!")
        
    except Exception as e:
        print(f"Error during main instruction test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_main_instruction_loading()