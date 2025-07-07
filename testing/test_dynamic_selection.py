#!/usr/bin/env python3
"""
Test script to verify dynamic template selection.
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

def test_dynamic_template_selection():
    """Test dynamic template selection functionality."""
    try:
        manager = InstructionManager()
        
        # Test 1: High difficulty data sufficiency
        print("=== Test 1: High Difficulty GMAT Data Sufficiency ===")
        prompt = "Arithmetic - Logical Reasoning - difficulty_level: 5"
        instruction = manager.get_optimized_instruction(
            ExamType.GMAT, 
            QuestionType.DATA_SUFFICIENCY, 
            prompt=prompt,
            difficulty_level=5
        )
        print(f"Instruction length: {len(instruction)} characters")
        if "HIGH DIFFICULTY EMPHASIS" in instruction:
            print("✓ High difficulty optimization applied")
        if "DATA SUFFICIENCY FOCUS" in instruction:
            print("✓ Data sufficiency optimization applied")
        if "GMAT BUSINESS CONTEXT" in instruction:
            print("✓ GMAT business context applied")
        
        # Test 2: Low difficulty with visual data
        print("\n=== Test 2: Low Difficulty GRE with Visual Data ===")
        prompt = "Statistics - Data Interpretation - pie chart - difficulty_level: 2"
        instruction = manager.get_optimized_instruction(
            ExamType.GRE, 
            QuestionType.PROBLEM_SOLVING, 
            prompt=prompt,
            difficulty_level=2
        )
        print(f"Instruction length: {len(instruction)} characters")
        if "FUNDAMENTAL LEVEL EMPHASIS" in instruction:
            print("✓ Low difficulty optimization applied")
        if "VISUAL DATA EMPHASIS" in instruction:
            print("✓ Visual data optimization applied")
        if "GRE ACADEMIC CONTEXT" in instruction:
            print("✓ GRE academic context applied")
        
        # Test 3: Reading comprehension (parent-child type)
        print("\n=== Test 3: Reading Comprehension Parent-Child ===")
        prompt = "Literature - Reading Comprehension - difficulty_level: 3"
        instruction = manager.get_optimized_instruction(
            ExamType.GMAT, 
            QuestionType.READING_COMPREHENSION, 
            prompt=prompt,
            difficulty_level=3
        )
        print(f"Instruction length: {len(instruction)} characters")
        if "PARENT-CHILD COORDINATION" in instruction:
            print("✓ Parent-child optimization applied")
        
        # Test 4: Logical reasoning emphasis
        print("\n=== Test 4: Logical Reasoning Emphasis ===")
        prompt = "Critical Reasoning - Logical Reasoning - difficulty_level: 4"
        instruction = manager.get_optimized_instruction(
            ExamType.GMAT, 
            QuestionType.CRITICAL_REASONING, 
            prompt=prompt,
            difficulty_level=4
        )
        if "LOGICAL REASONING EMPHASIS" in instruction:
            print("✓ Logical reasoning optimization applied")
        
        print("\nDynamic template selection test completed successfully!")
        
    except Exception as e:
        print(f"Error during dynamic selection test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dynamic_template_selection()