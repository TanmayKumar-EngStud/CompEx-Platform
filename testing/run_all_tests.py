#!/usr/bin/env python3
"""
Comprehensive test runner for Phase 4 Integration & Testing validation.
"""

import sys
import os
import time
from datetime import datetime

# Add the project root to path and change to project root directory
sys.path.append('..')
os.chdir('..')  # Change to project root directory

def run_test_with_header(test_name, test_function):
    """Run a test with proper header formatting."""
    print("=" * 80)
    print(f"🧪 RUNNING TEST: {test_name}")
    print("=" * 80)
    
    start_time = time.time()
    
    try:
        test_function()
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n✅ TEST PASSED: {test_name} (Duration: {duration:.2f}s)")
        return True
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n❌ TEST FAILED: {test_name} (Duration: {duration:.2f}s)")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all Phase 4 integration tests."""
    print("🚀 PHASE 4 INTEGRATION & TESTING - COMPREHENSIVE VALIDATION")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Set dummy API key to avoid errors in tests
    os.environ["API_0"] = "dummy_key_for_testing"
    
    test_results = []
    
    # Test 1: Main Instruction Loading
    print("\n🔧 Phase: Main Instruction Integration")
    sys.path.insert(0, 'testing')
    from test_main_instructions import test_main_instruction_loading
    result1 = run_test_with_header("Main Instruction Loading", test_main_instruction_loading)
    test_results.append(("Main Instruction Loading", result1))
    
    # Test 2: Dynamic Template Selection
    print("\n🎯 Phase: Dynamic Template Selection")
    from test_dynamic_selection import test_dynamic_template_selection
    result2 = run_test_with_header("Dynamic Template Selection", test_dynamic_template_selection)
    test_results.append(("Dynamic Template Selection", result2))
    
    # Test 3: Generator Integration
    print("\n🔗 Phase: Generator Integration")
    from test_generator_integration import test_generator_instruction_loading
    result3 = run_test_with_header("Generator Integration", test_generator_instruction_loading)
    test_results.append(("Generator Integration", result3))
    
    # Test 4: Philosophical Alignment
    print("\n🎓 Phase: Philosophical Alignment Validation")
    from test_philosophical_alignment import test_philosophical_alignment
    result4 = run_test_with_header("Philosophical Alignment", test_philosophical_alignment)
    test_results.append(("Philosophical Alignment", result4))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n📈 Success Rate: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 ALL TESTS PASSED! Phase 4 Integration & Testing completed successfully!")
        print("✅ Ready to proceed to Phase 5: Documentation & Finalization")
    elif success_rate >= 75:
        print("⚠️  Most tests passed, but some issues need attention")
    else:
        print("🚨 Multiple test failures - Phase 4 needs more work")
    
    print(f"\n🏁 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main()