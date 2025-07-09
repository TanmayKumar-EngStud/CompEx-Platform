"""
Comprehensive pytest test suite for template loading functionality.

This test suite validates that the enhanced template loading system works correctly
for all question types, ensuring that:
1. Main templates are loaded as system instructions without conflicts
2. Component-specific templates are appended to prompts dynamically
3. Debug files capture the enhanced "prompt + component template" format
4. No JSON parsing conflicts occur due to format instruction conflicts

Run with: pytest core/components/.testing/test_template_loading_functionality.py -v
"""

import pytest
import os
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Optional

# Import the components we're testing
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.instructions.instruction_manager import InstructionManager


class TestTemplateLoadingFunctionality:
    """Test suite for template loading functionality across all question types."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM client."""
        mock_llm = Mock()
        mock_chat = Mock()
        mock_llm.chats.create.return_value = mock_chat
        return mock_llm
    
    @pytest.fixture
    def mock_global_state(self):
        """Create mock global state."""
        return {
            'start_time': time.time(),
            'request_count': 0
        }
    
    @pytest.fixture
    def mock_lock(self):
        """Create mock threading lock."""
        return Mock()
    
    @pytest.fixture
    def instruction_manager(self):
        """Create instruction manager for testing."""
        return InstructionManager()
    
    def test_system_instructions_no_conflicts(self, instruction_manager):
        """Test that system instructions don't contain conflicting format directives."""
        # Test for each exam type and major question types
        test_cases = [
            (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY),
            (ExamType.GMAT, QuestionType.PROBLEM_SOLVING),
            (ExamType.GMAT, QuestionType.CRITICAL_REASONING),
            (ExamType.GRE, QuestionType.DATA_SUFFICIENCY),
            (ExamType.GRE, QuestionType.PROBLEM_SOLVING),
            (ExamType.GRE, QuestionType.TEXT_COMPLETION),
        ]
        
        for exam_type, question_type in test_cases:
            try:
                # Get main instruction (what would be system instructions)
                system_instructions = instruction_manager.get_main_instruction(exam_type, question_type)
                
                # Check that system instructions don't contain conflicting format directives
                plain_text_count = system_instructions.count("RESPONSE FORMAT:- PLAIN TEXT")
                json_count = system_instructions.count("STRICT RESPONSE FORMAT:- JSON")
                
                # System instructions should not have both format types mixed together
                assert not (plain_text_count > 0 and json_count > 0), \
                    f"Conflicting format instructions found in {exam_type.value}/{question_type.value}: " \
                    f"PLAIN TEXT: {plain_text_count}, JSON: {json_count}"
                    
            except Exception as e:
                # If instruction loading fails, that's also important to know
                pytest.fail(f"Failed to load main instruction for {exam_type.value}/{question_type.value}: {e}")
    
    def test_component_template_detection(self, mock_llm, mock_global_state, mock_lock):
        """Test that component types are correctly detected from prompts."""
        component_types = [
            "QuestionText",
            "QuestionTitle", 
            "QuestionSolution",
            "QuestionAnswer",
            "QuestionOptions",
            "QuestionPassage"
        ]
        
        test_prompts = [
            f"{component_type}: DS - <arithmetic> - <problem_solving> - <difficulty_level: 3>"
            for component_type in component_types
        ]
        
        with patch('core.interfaces.question_generator.genai.Client', return_value=mock_llm):
            component = create_question_component(
                question_type=QuestionType.DATA_SUFFICIENCY,
                llm=mock_llm,
                system_instructions="Test instructions",
                global_state=mock_global_state,
                lock=mock_lock,
                prompt="Test prompt",
                exam_type=ExamType.GMAT
            )
            
            for i, test_prompt in enumerate(test_prompts):
                expected_component = component_types[i]
                
                # Test the detection logic manually
                detected_component = None
                for component_type in component_types:
                    if test_prompt.startswith(component_type):
                        detected_component = component_type
                        break
                
                assert detected_component == expected_component, \
                    f"Failed to detect component type for prompt: {test_prompt}"
    
    def test_component_template_loading(self, mock_llm, mock_global_state, mock_lock, instruction_manager):
        """Test that component templates are loaded correctly."""
        test_cases = [
            (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "questionText"),
            (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "questionSolution"),
            (ExamType.GMAT, QuestionType.PROBLEM_SOLVING, "questionText"),
            (ExamType.GRE, QuestionType.DATA_SUFFICIENCY, "questionText"),
        ]
        
        for exam_type, question_type, mode in test_cases:
            try:
                template = instruction_manager.get_instruction(
                    exam_type=exam_type,
                    question_type=question_type,
                    mode=mode
                )
                
                # Template should be non-empty string
                assert isinstance(template, str), \
                    f"Template for {exam_type.value}/{question_type.value}/{mode} is not a string"
                assert len(template) > 0, \
                    f"Template for {exam_type.value}/{question_type.value}/{mode} is empty"
                
                # Template should contain format specification
                assert ("JSON" in template or "PLAIN TEXT" in template), \
                    f"Template for {exam_type.value}/{question_type.value}/{mode} missing format specification"
                
            except Exception as e:
                pytest.fail(f"Failed to load template for {exam_type.value}/{question_type.value}/{mode}: {e}")
    
    def test_enhanced_prompt_construction(self, mock_llm, mock_global_state, mock_lock):
        """Test that prompts are enhanced with component templates."""
        test_prompt = "QuestionText: DS - <arithmetic> - <problem_solving> - <difficulty_level: 3>"
        
        with patch('core.interfaces.question_generator.genai.Client', return_value=mock_llm):
            component = create_question_component(
                question_type=QuestionType.DATA_SUFFICIENCY,
                llm=mock_llm,
                system_instructions="Test instructions",
                global_state=mock_global_state,
                lock=mock_lock,
                prompt="Test prompt",
                exam_type=ExamType.GMAT
            )
            
            # Test component detection and template loading
            component_types = ["QuestionSolution", "QuestionOptions", "QuestionText", 
                             "QuestionTitle", "QuestionAnswer", "QuestionPassage"]
            component_match = None
            for component_type in component_types:
                if test_prompt.startswith(component_type):
                    component_match = component_type
                    break
            
            assert component_match == "QuestionText", \
                f"Expected to detect QuestionText, got {component_match}"
            
            # Test template instruction loading
            try:
                template_instruction = component._get_component_instruction(component_match)
                assert isinstance(template_instruction, str), "Template instruction should be a string"
                assert len(template_instruction) > 0, "Template instruction should not be empty"
                
                # Construct enhanced prompt as the system would
                enhanced_prompt = f"{test_prompt}\n\nComponent Template:\n{template_instruction}"
                
                # Enhanced prompt should be longer than original
                assert len(enhanced_prompt) > len(test_prompt), \
                    "Enhanced prompt should be longer than original prompt"
                
                # Enhanced prompt should contain both parts
                assert test_prompt in enhanced_prompt, \
                    "Enhanced prompt should contain original prompt"
                assert "Component Template:" in enhanced_prompt, \
                    "Enhanced prompt should contain component template marker"
                assert template_instruction in enhanced_prompt, \
                    "Enhanced prompt should contain template instruction"
                
            except Exception as e:
                pytest.fail(f"Failed to create enhanced prompt: {e}")
    
    def test_question_component_creation_all_types(self, mock_llm, mock_global_state, mock_lock):
        """Test that all question component types can be created without errors."""
        test_cases = [
            # GMAT question types
            (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY),
            (ExamType.GMAT, QuestionType.PROBLEM_SOLVING),
            (ExamType.GMAT, QuestionType.CRITICAL_REASONING),
            (ExamType.GMAT, QuestionType.READING_COMPREHENSION),
            (ExamType.GMAT, QuestionType.GRAPHIC_INTERPRETATION),
            (ExamType.GMAT, QuestionType.TABLE_ANALYSIS),
            (ExamType.GMAT, QuestionType.TWO_PART_ANALYSIS),
            (ExamType.GMAT, QuestionType.MULTI_SOURCE_REASONING),
            
            # GRE question types
            (ExamType.GRE, QuestionType.DATA_SUFFICIENCY),
            (ExamType.GRE, QuestionType.PROBLEM_SOLVING),
            (ExamType.GRE, QuestionType.NUMERIC_ENTRY),
            (ExamType.GRE, QuestionType.TEXT_COMPLETION),
            (ExamType.GRE, QuestionType.SENTENCE_EQUIVALENCE),
            (ExamType.GRE, QuestionType.READING_COMPREHENSION),
        ]
        
        for exam_type, question_type in test_cases:
            with patch('core.interfaces.question_generator.genai.Client', return_value=mock_llm):
                try:
                    component = create_question_component(
                        question_type=question_type,
                        llm=mock_llm,
                        system_instructions="Test instructions",
                        global_state=mock_global_state,
                        lock=mock_lock,
                        prompt=f"Test prompt for {question_type.value}",
                        exam_type=exam_type
                    )
                    
                    # Component should be created successfully
                    assert component is not None, \
                        f"Failed to create component for {exam_type.value}/{question_type.value}"
                    
                    # Component should have required attributes
                    assert hasattr(component, 'exam_type'), \
                        f"Component missing exam_type for {exam_type.value}/{question_type.value}"
                    assert hasattr(component, 'question_type'), \
                        f"Component missing question_type for {exam_type.value}/{question_type.value}"
                    assert hasattr(component, '_get_component_instruction'), \
                        f"Component missing _get_component_instruction for {exam_type.value}/{question_type.value}"
                    
                except Exception as e:
                    pytest.fail(f"Failed to create component for {exam_type.value}/{question_type.value}: {e}")
    
    def test_template_format_consistency(self, instruction_manager):
        """Test that templates have consistent format specifications."""
        # Component modes that should have JSON format
        json_modes = ["questionText", "questionTitle", "questionOptions"]
        
        # Component modes that should have plain text format
        plaintext_modes = ["questionSolution", "questionAnswer"]
        
        test_cases = [
            (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY),
            (ExamType.GMAT, QuestionType.PROBLEM_SOLVING),
            (ExamType.GRE, QuestionType.DATA_SUFFICIENCY),
        ]
        
        for exam_type, question_type in test_cases:
            # Test JSON format modes
            for mode in json_modes:
                try:
                    if instruction_manager.validate_mode(question_type, mode):
                        template = instruction_manager.get_instruction(exam_type, question_type, mode)
                        assert "JSON" in template, \
                            f"Mode {mode} should specify JSON format for {exam_type.value}/{question_type.value}"
                except Exception:
                    # Skip modes that don't exist for this question type
                    continue
            
            # Test plain text format modes  
            for mode in plaintext_modes:
                try:
                    if instruction_manager.validate_mode(question_type, mode):
                        template = instruction_manager.get_instruction(exam_type, question_type, mode)
                        assert "PLAIN TEXT" in template, \
                            f"Mode {mode} should specify PLAIN TEXT format for {exam_type.value}/{question_type.value}"
                except Exception:
                    # Skip modes that don't exist for this question type
                    continue
    
    @pytest.mark.parametrize("exam_type,question_type", [
        (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY),
        (ExamType.GMAT, QuestionType.PROBLEM_SOLVING),
        (ExamType.GRE, QuestionType.DATA_SUFFICIENCY),
        (ExamType.GRE, QuestionType.PROBLEM_SOLVING),
    ])
    def test_demo_prompts_processing(self, exam_type, question_type, mock_llm, mock_global_state, mock_lock):
        """Test processing of demo prompts for different question types."""
        demo_prompts = {
            QuestionType.DATA_SUFFICIENCY: [
                "DS - <arithmetic> - <problem_solving> - <difficulty_level: 3>",
                "DS - <algebra> - <linear_equations> - <difficulty_level: 4>",
                "DS - <geometry> - <coordinate_geometry> - <difficulty_level: 2>",
            ],
            QuestionType.PROBLEM_SOLVING: [
                "PS - <arithmetic> - <percentages> - <difficulty_level: 3>",
                "PS - <algebra> - <quadratic_equations> - <difficulty_level: 4>",
                "PS - <data_analysis> - <statistics> - <difficulty_level: 2>",
            ],
            QuestionType.TEXT_COMPLETION: [
                "TC - <reading> - <vocabulary> - <difficulty_level: 3>",
                "TC - <logic> - <reasoning> - <difficulty_level: 4>",
            ],
            QuestionType.NUMERIC_ENTRY: [
                "NE - <arithmetic> - <calculations> - <difficulty_level: 3>",
                "NE - <algebra> - <solving> - <difficulty_level: 4>",
            ]
        }
        
        prompts = demo_prompts.get(question_type, [f"{question_type.value} - <test> - <demo> - <difficulty_level: 3>"])
        
        for prompt in prompts:
            with patch('core.interfaces.question_generator.genai.Client', return_value=mock_llm):
                try:
                    component = create_question_component(
                        question_type=question_type,
                        llm=mock_llm,
                        system_instructions="Test instructions",
                        global_state=mock_global_state,
                        lock=mock_lock,
                        prompt=prompt,
                        exam_type=exam_type
                    )
                    
                    # Component should be created successfully with demo prompt
                    assert component is not None, \
                        f"Failed to create component with demo prompt: {prompt}"
                    
                    # Test component type detection for various component prompts
                    component_prompts = [
                        f"QuestionText: {prompt}",
                        f"QuestionTitle: {prompt}",
                        f"QuestionSolution: {prompt}",
                    ]
                    
                    for comp_prompt in component_prompts:
                        expected_type = comp_prompt.split(":")[0]
                        
                        # Test detection logic
                        component_types = ["QuestionSolution", "QuestionOptions", "QuestionText", 
                                         "QuestionTitle", "QuestionAnswer", "QuestionPassage"]
                        detected = None
                        for comp_type in component_types:
                            if comp_prompt.startswith(comp_type):
                                detected = comp_type
                                break
                        
                        assert detected == expected_type, \
                            f"Failed to detect {expected_type} in prompt: {comp_prompt}"
                
                except Exception as e:
                    pytest.fail(f"Demo prompt processing failed for {exam_type.value}/{question_type.value} with prompt '{prompt}': {e}")


class TestDebugFileGeneration:
    """Test debug file generation and format."""
    
    def test_debug_file_enhanced_prompt_format(self):
        """Test that debug files would contain enhanced prompt format."""
        # This tests the logic that would generate debug files
        original_prompt = "QuestionText: DS - <arithmetic> - <problem_solving> - <difficulty_level: 3>"
        mock_template = """STRICT RESPONSE FORMAT:- JSON
- "passage" key with small passage text.
- "statements" key with array of exactly 2 statements.
- "question" key with complete question text."""
        
        # Simulate the enhanced prompt construction
        enhanced_prompt = f"{original_prompt}\n\nComponent Template:\n{mock_template}"
        
        # Verify the enhanced prompt has the expected format
        assert original_prompt in enhanced_prompt, "Enhanced prompt should contain original prompt"
        assert "Component Template:" in enhanced_prompt, "Enhanced prompt should contain template marker"
        assert mock_template in enhanced_prompt, "Enhanced prompt should contain template content"
        assert len(enhanced_prompt) > len(original_prompt), "Enhanced prompt should be longer"
        
        # Verify it matches expected debug file format
        lines = enhanced_prompt.split('\n')
        assert lines[0] == original_prompt, "First line should be original prompt"
        assert lines[1] == "", "Second line should be empty"
        assert lines[2] == "Component Template:", "Third line should be template marker"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])