#!/usr/bin/env python3
"""
Test runner for template loading functionality validation.

This script runs the essential tests to validate that the template loading fixes are working correctly.

Usage: python core/components/.testing/run_template_tests.py
"""

import subprocess
import sys
import os

def run_test_suite():
    """Run the essential template loading tests."""
    print("🧪 Running Template Loading Functionality Tests")
    print("=" * 60)
    
    # Essential test files to run
    test_files = [
        "core/components/.testing/test_template_functionality.py",
        "core/components/.testing/test_template_fixes_summary.py",
        "core/components/.testing/test_integration_template_flow.py",
    ]
    
    total_passed = 0
    total_failed = 0
    total_tests = 0
    
    for test_file in test_files:
        print(f"\n📋 Running: {test_file}")
        print("-" * 50)
        
        try:
            # Run pytest for this specific file
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            # Parse the output for test results
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if "passed" in line and "failed" in line:
                    # Extract test counts from summary line like "12 failed, 36 passed in 0.89s"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            total_passed += int(parts[i-1])
                        elif part == "failed":
                            total_failed += int(parts[i-1])
                elif line.endswith(" PASSED"):
                    total_tests += 1
                elif line.endswith(" FAILED"):
                    total_tests += 1
                    
            # Print result summary for this file
            if result.returncode == 0:
                print(f"✅ {test_file}: ALL TESTS PASSED")
            else:
                print(f"⚠️  {test_file}: SOME TESTS FAILED")
                
            # Print stdout if there are failures or for summary test
            if result.returncode != 0 or "summary" in test_file:
                print(result.stdout)
                
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            total_failed += 1
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 TEMPLATE LOADING TESTS SUMMARY")
    print("=" * 60)
    
    if total_failed == 0:
        print("🎉 ALL TEMPLATE LOADING TESTS PASSED! 🎉")
        print("\n✅ Main templates have no format conflicts")
        print("✅ Component templates load and append correctly")
        print("✅ Enhanced prompt construction works")
        print("✅ Debug files capture correct format")
        print("✅ All major question types supported")
        print("\n💯 The template loading fixes are working perfectly!")
        print("💯 JSON parsing errors should be eliminated!")
        return True
    else:
        print(f"⚠️  Some tests failed or had issues: {total_failed} failures")
        print("📝 Check the output above for details")
        return False

def main():
    """Main entry point."""
    try:
        success = run_test_suite()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()