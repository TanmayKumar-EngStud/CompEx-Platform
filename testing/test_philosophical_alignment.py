#!/usr/bin/env python3
"""
Test script to validate philosophical alignment of the new template system.
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

def test_philosophical_alignment():
    """Test that the new template system aligns with educational philosophy."""
    try:
        manager = InstructionManager()
        
        # Core philosophical principles to validate
        core_principles = [
            "trap-based option generation",
            "realistic, educationally sound",
            "assess specific cognitive skills",
            "differentiate between students",
            "common mistakes",
            "authentic, exam-level",
            "skill-focused assessment",
            "mistake anticipation"
        ]
        
        # Question types to test
        test_cases = [
            (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "Arithmetic - Logical Reasoning - difficulty_level: 4"),
            (ExamType.GRE, QuestionType.NUMERIC_ENTRY, "Algebra - Problem Solving - difficulty_level: 3"),
            (ExamType.GMAT, QuestionType.READING_COMPREHENSION, "Literature - Reading Comprehension - difficulty_level: 2"),
            (ExamType.GRE, QuestionType.TEXT_COMPLETION, "Vocabulary - Text Completion - difficulty_level: 5")
        ]
        
        print("=== PHILOSOPHICAL ALIGNMENT VALIDATION ===\n")
        
        alignment_scores = {}
        
        for exam_type, question_type, prompt in test_cases:
            print(f"Testing {exam_type.value} {question_type.value}")
            print(f"Prompt: {prompt}")
            
            # Get optimized instruction
            instruction = manager.get_optimized_instruction(
                exam_type, question_type, prompt, 
                difficulty_level=int(prompt.split("difficulty_level: ")[1])
            )
            
            # Check for core philosophical principles
            principles_found = 0
            principles_details = []
            
            for principle in core_principles:
                if principle.lower() in instruction.lower():
                    principles_found += 1
                    principles_details.append(f"✓ {principle}")
                else:
                    principles_details.append(f"✗ {principle}")
            
            # Calculate alignment score
            alignment_percentage = (principles_found / len(core_principles)) * 100
            alignment_scores[f"{exam_type.value}_{question_type.value}"] = alignment_percentage
            
            print(f"Alignment Score: {alignment_percentage:.1f}% ({principles_found}/{len(core_principles)})")
            
            # Show detailed results
            for detail in principles_details:
                print(f"  {detail}")
            
            # Test specific philosophy elements for each question type
            print("  Question-Specific Philosophy:")
            if question_type == QuestionType.DATA_SUFFICIENCY:
                if "sufficiency analysis" in instruction.lower():
                    print("  ✓ Data Sufficiency: Emphasizes sufficiency over computation")
                if "business" in instruction.lower() and exam_type == ExamType.GMAT:
                    print("  ✓ GMAT: Business context emphasis")
                if "academic" in instruction.lower() and exam_type == ExamType.GRE:
                    print("  ✓ GRE: Academic context emphasis")
            
            if question_type == QuestionType.READING_COMPREHENSION:
                if "parent-child coordination" in instruction.lower():
                    print("  ✓ RC: Parent-child structure guidance")
            
            if "high difficulty emphasis" in instruction.lower():
                print("  ✓ High Difficulty: Sophisticated trap emphasis")
            elif "fundamental level emphasis" in instruction.lower():
                print("  ✓ Low Difficulty: Fundamental concept emphasis")
            
            print()
        
        # Overall validation summary
        print("=== OVERALL VALIDATION SUMMARY ===")
        
        average_alignment = sum(alignment_scores.values()) / len(alignment_scores)
        print(f"Average Philosophical Alignment: {average_alignment:.1f}%")
        
        if average_alignment >= 90:
            print("🟢 EXCELLENT: Strong philosophical alignment")
        elif average_alignment >= 75:
            print("🟡 GOOD: Acceptable philosophical alignment")
        else:
            print("🔴 NEEDS IMPROVEMENT: Weak philosophical alignment")
        
        # Test template inheritance
        print("\n=== TEMPLATE INHERITANCE VALIDATION ===")
        
        # Check if generic philosophy is being inherited
        ds_instruction = manager.get_main_instruction(ExamType.GMAT, QuestionType.DATA_SUFFICIENCY)
        if "Universal Question Generation Philosophy" in ds_instruction:
            print("✓ Template inheritance working: Generic philosophy found in specific templates")
        else:
            print("✗ Template inheritance issue: Generic philosophy not found")
        
        # Test conditional processing
        print("\n=== CONDITIONAL PROCESSING VALIDATION ===")
        
        gmat_instruction = manager.get_optimized_instruction(ExamType.GMAT, QuestionType.DATA_SUFFICIENCY)
        gre_instruction = manager.get_optimized_instruction(ExamType.GRE, QuestionType.DATA_SUFFICIENCY)
        
        if "GMAT BUSINESS CONTEXT" in gmat_instruction and "GRE ACADEMIC CONTEXT" in gre_instruction:
            print("✓ Conditional processing working: Exam-specific content properly applied")
        else:
            print("✗ Conditional processing issue: Exam-specific content not properly applied")
        
        print("\nPhilosophical alignment validation completed!")
        
    except Exception as e:
        print(f"Error during philosophical alignment test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_philosophical_alignment()