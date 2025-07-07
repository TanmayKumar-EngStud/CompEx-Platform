#!/usr/bin/env python3
"""
Test script for the graph style management system.

This script validates that the graph style system can parse graph types
from prompts and inject appropriate styles into instruction templates.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.instructions.graph_style_manager import GraphStyleManager
from core.instructions.instruction_manager import InstructionManager


def test_graph_style_manager():
    """Test graph style manager functionality."""
    print("🎨 Testing Graph Style Manager")
    print("=" * 50)
    
    try:
        manager = GraphStyleManager()
        print("✅ GraphStyleManager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize GraphStyleManager: {e}")
        return False
    
    # Test graph type parsing
    test_prompts = [
        "GI - <Economics> - <Data Interpretation> - <Bar Chart> - <difficulty_level: 2>",
        "Create a pie chart showing market distribution",
        "Generate a line graph for quarterly sales",
        "GI - <Finance> - <Analysis> - <Scatter Plot> - <difficulty_level: 4>",
        "Show data using horizontal bar chart format",
        "Display trends with area chart visualization"
    ]
    
    print(f"\n🔍 Testing graph type parsing from {len(test_prompts)} prompts...")
    
    parsing_success = 0
    for i, prompt in enumerate(test_prompts, 1):
        try:
            graph_type = manager.parse_graph_type_from_prompt(prompt)
            if graph_type:
                print(f"{i:2d}. ✅ Parsed '{graph_type}' from: {prompt[:50]}...")
                parsing_success += 1
            else:
                print(f"{i:2d}. ⚠️  No graph type found in: {prompt[:50]}...")
        except Exception as e:
            print(f"{i:2d}. ❌ Error parsing: {e}")
    
    print(f"\n📊 Parsing Results: {parsing_success}/{len(test_prompts)} prompts parsed successfully")
    
    # Test style retrieval
    print(f"\n🎯 Testing style retrieval...")
    
    test_graph_types = ["bar_chart", "pie_chart", "line_chart", "scatter_plot"]
    style_success = 0
    
    for graph_type in test_graph_types:
        try:
            style = manager.get_graph_style(graph_type)
            if style:
                print(f"   ✅ {graph_type}: Style loaded with {len(style)} properties")
                style_success += 1
            else:
                print(f"   ⚠️  {graph_type}: No style found")
        except Exception as e:
            print(f"   ❌ {graph_type}: Error loading style - {e}")
    
    print(f"\n📊 Style Results: {style_success}/{len(test_graph_types)} styles loaded successfully")
    
    # Test system info
    print(f"\n🔧 System Information:")
    system_info = manager.get_system_info()
    for key, value in system_info.items():
        print(f"   {key}: {value}")
    
    return parsing_success > 0 and style_success > 0


def test_instruction_integration():
    """Test graph style integration with instruction system."""
    print(f"\n🔌 Testing Instruction System Integration")
    print("-" * 40)
    
    try:
        instruction_manager = InstructionManager()
        print("✅ InstructionManager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize InstructionManager: {e}")
        return False
    
    # Test prompts with different graph types
    test_cases = [
        {
            "prompt": "GI - <Economics> - <Data Interpretation> - <Bar Chart> - <difficulty_level: 3>",
            "exam_type": ExamType.GMAT,
            "question_type": QuestionType.GRAPHIC_INTERPRETATION,
            "mode": "questionGraph"
        },
        {
            "prompt": "Create a pie chart for market analysis",
            "exam_type": ExamType.GMAT,
            "question_type": QuestionType.GRAPHIC_INTERPRETATION,
            "mode": "questionGraph"
        },
        {
            "prompt": "Generate line chart showing trends",
            "exam_type": ExamType.GMAT,
            "question_type": QuestionType.GRAPHIC_INTERPRETATION,
            "mode": "questionGraph"
        }
    ]
    
    integration_success = 0
    for i, test_case in enumerate(test_cases, 1):
        try:
            instruction = instruction_manager.get_instruction(
                test_case["exam_type"],
                test_case["question_type"],
                test_case["mode"],
                test_case["prompt"]
            )
            
            if instruction and len(instruction.strip()) > 0:
                # Check if graph style placeholders were replaced
                has_graph_info = any(placeholder in instruction for placeholder in [
                    "GRAPH_DISPLAY_INSTRUCTIONS",
                    "GRAPH_JSON_FORMAT", 
                    "GRAPH_STRUCTURE_EXAMPLE"
                ])
                
                if not has_graph_info:
                    print(f"{i:2d}. ✅ Instruction generated with graph styles ({len(instruction)} chars)")
                    integration_success += 1
                else:
                    print(f"{i:2d}. ⚠️  Instruction generated but graph placeholders not replaced")
            else:
                print(f"{i:2d}. ⚠️  Empty instruction returned")
                
        except Exception as e:
            print(f"{i:2d}. ❌ Error: {e}")
    
    print(f"\n📊 Integration Results: {integration_success}/{len(test_cases)} tests passed")
    
    return integration_success > 0


def test_style_injection():
    """Test graph style injection into templates."""
    print(f"\n💉 Testing Style Injection")
    print("-" * 30)
    
    try:
        manager = GraphStyleManager()
        
        # Test template with placeholders
        test_template = """
        Graph Generation Instructions:
        
        {{GRAPH_DISPLAY_INSTRUCTIONS}}
        
        Required Format:
        {{GRAPH_JSON_FORMAT}}
        
        Example Structure:
        {{GRAPH_STRUCTURE_EXAMPLE}}
        """
        
        test_prompts = [
            "Create a bar chart for sales data",
            "Generate pie chart showing distribution",
            "Show scatter plot of correlation"
        ]
        
        injection_success = 0
        for i, prompt in enumerate(test_prompts, 1):
            try:
                result = manager.inject_graph_style(test_template, prompt)
                
                # Check if placeholders were replaced
                has_placeholders = any(placeholder in result for placeholder in [
                    "{{GRAPH_DISPLAY_INSTRUCTIONS}}",
                    "{{GRAPH_JSON_FORMAT}}", 
                    "{{GRAPH_STRUCTURE_EXAMPLE}}"
                ])
                
                if not has_placeholders and len(result) > len(test_template):
                    print(f"{i:2d}. ✅ Style injection successful ({len(result)} chars)")
                    injection_success += 1
                else:
                    print(f"{i:2d}. ⚠️  Style injection incomplete or failed")
                    
            except Exception as e:
                print(f"{i:2d}. ❌ Injection error: {e}")
        
        print(f"\n📊 Injection Results: {injection_success}/{len(test_prompts)} injections successful")
        
        return injection_success > 0
        
    except Exception as e:
        print(f"❌ Style injection test failed: {e}")
        return False


def main():
    """Main test runner."""
    print("🚀 Starting Graph Style System Tests")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    test_results.append(("Graph Style Manager", test_graph_style_manager()))
    test_results.append(("Instruction Integration", test_instruction_integration()))
    test_results.append(("Style Injection", test_style_injection()))
    
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
        print("🎉 All tests passed! Graph style system is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())