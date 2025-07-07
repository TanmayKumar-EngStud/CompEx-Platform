#!/usr/bin/env python3
"""
Test script for the new instruction management system.

This script validates that the instruction system is working properly
and can load instructions for various question types and exam types.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.instructions.instruction_manager import InstructionManager


def test_instruction_loading():
    """Test instruction loading for various combinations."""
    print("🧪 Testing Instruction Management System")
    print("=" * 50)
    
    # Initialize instruction manager
    try:
        manager = InstructionManager()
        print("✅ InstructionManager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize InstructionManager: {e}")
        return False
    
    # Test combinations to check
    test_cases = [
        (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "questionText"),
        (ExamType.GRE, QuestionType.DATA_SUFFICIENCY, "questionText"),
        (ExamType.GMAT, QuestionType.CRITICAL_REASONING, "questionPassage"),
        (ExamType.GMAT, QuestionType.GRAPHIC_INTERPRETATION, "questionGraph"),
        (ExamType.GRE, QuestionType.NUMERIC_ENTRY, "questionText"),
        (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "questionTitle"),
        (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "questionSolution"),
        (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "questionAnswer"),
    ]
    
    print(f"\n🔍 Testing {len(test_cases)} instruction loading scenarios...")
    
    success_count = 0
    for i, (exam_type, question_type, mode) in enumerate(test_cases, 1):
        try:
            print(f"\n{i:2d}. Testing: {exam_type.value} {question_type.value} {mode}")
            
            instruction = manager.get_instruction(exam_type, question_type, mode)
            
            if instruction and len(instruction.strip()) > 0:
                print(f"    ✅ Success - {len(instruction)} characters loaded")
                print(f"    📝 Preview: {instruction[:100]}...")
                success_count += 1
            else:
                print(f"    ⚠️  Empty instruction returned")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    print(f"\n📊 Results: {success_count}/{len(test_cases)} tests passed")
    
    # Test system info
    print(f"\n🔧 System Information:")
    system_info = manager.get_system_info()
    for key, value in system_info.items():
        print(f"   {key}: {value}")
    
    # Test cache info
    print(f"\n💾 Cache Information:")
    cache_info = manager.get_cache_info()
    for key, value in cache_info.items():
        print(f"   {key}: {value}")
    
    return success_count == len(test_cases)


def test_unified_mode_only():
    """Test that the system works in unified mode only (no legacy fallback)."""
    print(f"\n🔄 Testing Unified Mode Only")
    print("-" * 30)
    
    # Verify that old legacy files have been properly removed
    legacy_paths = [
        "GMAT/Quants/System_instructions/GMAT-Quants-Data-Sufficiency-Questions.txt",
        "GRE/Quants/System_instructions/GRE-Quants-Data-Sufficiency-Questions.txt"
    ]
    
    legacy_removed = 0
    for path in legacy_paths:
        full_path = project_root / path
        if not full_path.exists():
            legacy_removed += 1
            print(f"   ✅ Legacy file properly removed: {path}")
        else:
            print(f"   ⚠️  Legacy file still exists: {path}")
    
    print(f"   📊 Legacy files removed: {legacy_removed}/{len(legacy_paths)}")
    
    # Test that the system works purely with unified instruction management
    try:
        from core.instructions.instruction_manager import InstructionManager
        manager = InstructionManager()
        
        # Test a few instructions to ensure unified mode is working
        instruction = manager.get_instruction(
            ExamType.GMAT, 
            QuestionType.DATA_SUFFICIENCY, 
            "questionText"
        )
        
        if instruction and len(instruction) > 0:
            print(f"   ✅ Unified instruction system functional")
            return True
        else:
            print(f"   ❌ Unified instruction system not working")
            return False
            
    except Exception as e:
        print(f"   ❌ Unified instruction system error: {e}")
        return False


def test_generator_integration():
    """Test that generators can use the new instruction system."""
    print(f"\n🔌 Testing Generator Integration")
    print("-" * 30)
    
    try:
        from core.interfaces.question_generator import BaseQuestionGenerator
        
        # Create a test generator instance
        class TestGenerator(BaseQuestionGenerator):
            def generate_question(self, prompt):
                return {"test": "question"}
            
            def validate_output(self, question_data):
                return True
        
        # Test initialization with new instruction system
        generator = TestGenerator(
            exam_type=ExamType.GMAT,
            question_type=QuestionType.DATA_SUFFICIENCY,
            prompt="Test prompt"
        )
        
        print("   ✅ Generator initialized successfully")
        
        # Test instruction loading for different modes
        modes_to_test = ["questionText", "questionTitle", "questionSolution", "questionAnswer"]
        for mode in modes_to_test:
            try:
                instruction = generator.get_instruction_for_mode(mode)
                if instruction and len(instruction.strip()) > 0:
                    print(f"   ✅ Mode '{mode}': {len(instruction)} characters")
                else:
                    print(f"   ⚠️  Mode '{mode}': Empty or None")
            except Exception as e:
                print(f"   ❌ Mode '{mode}': {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Generator integration test failed: {e}")
        return False


def main():
    """Main test runner."""
    print("🚀 Starting Instruction System Tests")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    test_results.append(("Instruction Loading", test_instruction_loading()))
    test_results.append(("Unified Mode Only", test_unified_mode_only()))
    test_results.append(("Generator Integration", test_generator_integration()))
    
    # Summary
    print(f"\n🏁 Test Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25s} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("🎉 All tests passed! Instruction system is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())