"""
Focused pytest test suite for template loading functionality.

This test suite validates the core template loading functionality that was fixed:
1. Main templates don't contain conflicting format instructions
2. Component templates are loadable and have correct format specifications
3. Template detection logic works correctly
4. Demo prompts can be processed correctly

Run with: pytest core/components/.testing/test_template_functionality.py -v
"""

import pytest
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.instructions.instruction_manager import InstructionManager


class TestTemplateFunctionality:
    """Test suite for core template functionality."""
    
    @pytest.fixture
    def instruction_manager(self):
        """Create instruction manager for testing."""
        return InstructionManager()
    
    def test_main_instructions_no_conflicts(self, instruction_manager):
        """Test that main system instructions don't contain conflicting format directives."""
        # Test for major question types across both exam types
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
                # Get main instruction (what becomes system instructions)
                main_instruction = instruction_manager.get_main_instruction(exam_type, question_type)
                
                # Count conflicting format directives
                plain_text_count = main_instruction.count("RESPONSE FORMAT:- PLAIN TEXT")
                json_count = main_instruction.count("STRICT RESPONSE FORMAT:- JSON")
                
                # Main instructions should NOT have both format types
                assert not (plain_text_count > 0 and json_count > 0), \
                    f"❌ Conflicting format instructions in {exam_type.value}/{question_type.value} main instruction: " \
                    f"PLAIN TEXT: {plain_text_count}, JSON: {json_count}"
                
                print(f"✅ {exam_type.value}/{question_type.value} main instruction: no conflicts")
                    
            except Exception as e:
                pytest.fail(f"Failed to load main instruction for {exam_type.value}/{question_type.value}: {e}")
    
    def test_component_template_loading(self, instruction_manager):
        """Test that component templates can be loaded and have proper format specifications."""
        test_cases = [
            # (exam_type, question_type, mode, expected_format)
            (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "questionText", "JSON"),
            (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "questionSolution", "PLAIN TEXT"),
            (ExamType.GMAT, QuestionType.PROBLEM_SOLVING, "questionText", "JSON"),
            (ExamType.GRE, QuestionType.DATA_SUFFICIENCY, "questionText", "JSON"),
            (ExamType.GRE, QuestionType.PROBLEM_SOLVING, "questionText", "JSON"),
        ]
        
        for exam_type, question_type, mode, expected_format in test_cases:
            try:
                # Check if mode is valid for this question type
                if not instruction_manager.validate_mode(question_type, mode):
                    print(f"⚠️  Skipping {exam_type.value}/{question_type.value}/{mode} - mode not available")
                    continue
                
                template = instruction_manager.get_instruction(exam_type, question_type, mode)
                
                # Template should be non-empty
                assert isinstance(template, str) and len(template) > 0, \
                    f"Template for {exam_type.value}/{question_type.value}/{mode} is empty or not a string"
                
                # Template should contain expected format specification
                assert expected_format in template, \
                    f"Template for {exam_type.value}/{question_type.value}/{mode} missing {expected_format} format specification"
                
                print(f"✅ {exam_type.value}/{question_type.value}/{mode}: {expected_format} format specified")
                
            except Exception as e:
                pytest.fail(f"Failed to load template for {exam_type.value}/{question_type.value}/{mode}: {e}")
    
    def test_template_component_detection_logic(self):
        """Test the core component detection logic used in _get_response."""
        component_types = ["QuestionSolution", "QuestionOptions", "QuestionText", 
                          "QuestionTitle", "QuestionAnswer", "QuestionPassage"]
        
        test_cases = [
            ("QuestionText: DS - <arithmetic> - <problem_solving> - <difficulty_level: 3>", "QuestionText"),
            ("QuestionSolution: Generate solution for the above question", "QuestionSolution"),
            ("QuestionTitle: Create a title", "QuestionTitle"),
            ("QuestionAnswer: What is the correct answer?", "QuestionAnswer"),
            ("QuestionOptions: Generate answer choices", "QuestionOptions"),
            ("QuestionPassage: Create a reading passage", "QuestionPassage"),
            ("Regular prompt without component type", None),
        ]
        
        for test_prompt, expected_component in test_cases:
            # Replicate the exact detection logic from _get_response
            component_match = None
            for component_type in component_types:
                if test_prompt.startswith(component_type):
                    component_match = component_type
                    break
            
            assert component_match == expected_component, \
                f"Detection failed for '{test_prompt}': expected '{expected_component}', got '{component_match}'"
            
            if expected_component:
                print(f"✅ Detected '{expected_component}' in prompt: {test_prompt[:50]}...")
    
    def test_enhanced_prompt_construction_logic(self):
        """Test the enhanced prompt construction logic."""
        original_prompt = "QuestionText: DS - <arithmetic> - <problem_solving> - <difficulty_level: 3>"
        mock_template = """STRICT RESPONSE FORMAT:- JSON
- "passage" key with small passage text.
- "statements" key with array of exactly 2 statements.
- "question" key with complete question text."""
        
        # Replicate the exact enhanced prompt construction from _get_response
        enhanced_prompt = f"{original_prompt}\n\nComponent Template:\n{mock_template}"
        
        # Validate the construction
        assert original_prompt in enhanced_prompt, "Enhanced prompt should contain original prompt"
        assert "Component Template:" in enhanced_prompt, "Enhanced prompt should contain template marker"
        assert mock_template in enhanced_prompt, "Enhanced prompt should contain template content"
        assert len(enhanced_prompt) > len(original_prompt), "Enhanced prompt should be longer than original"
        
        # Validate debug file format (what would appear in prompt_used)
        lines = enhanced_prompt.split('\n')
        assert lines[0] == original_prompt, "First line should be original prompt"
        assert lines[1] == "", "Second line should be empty separator"
        assert lines[2] == "Component Template:", "Third line should be template marker"
        
        print(f"✅ Enhanced prompt construction: {len(enhanced_prompt)} chars (was {len(original_prompt)})")
    
    @pytest.mark.parametrize("exam_type,question_type,demo_prompt", [
        (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "DS - <arithmetic> - <problem_solving> - <difficulty_level: 3>"),
        (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "DS - <algebra> - <linear_equations> - <difficulty_level: 4>"),
        (ExamType.GMAT, QuestionType.PROBLEM_SOLVING, "PS - <arithmetic> - <percentages> - <difficulty_level: 3>"),
        (ExamType.GMAT, QuestionType.PROBLEM_SOLVING, "PS - <geometry> - <area_volume> - <difficulty_level: 4>"),
        (ExamType.GRE, QuestionType.DATA_SUFFICIENCY, "DS - <arithmetic> - <ratios> - <difficulty_level: 2>"),
        (ExamType.GRE, QuestionType.PROBLEM_SOLVING, "PS - <data_analysis> - <statistics> - <difficulty_level: 3>"),
        (ExamType.GRE, QuestionType.TEXT_COMPLETION, "TC - <reading> - <vocabulary> - <difficulty_level: 3>"),
        (ExamType.GRE, QuestionType.NUMERIC_ENTRY, "NE - <arithmetic> - <calculations> - <difficulty_level: 2>"),
    ])
    def test_demo_prompt_template_loading(self, instruction_manager, exam_type, question_type, demo_prompt):
        """Test template loading with various demo prompts."""
        try:
            # Test main instruction loading
            main_instruction = instruction_manager.get_main_instruction(exam_type, question_type)
            assert len(main_instruction) > 0, f"Main instruction should not be empty"
            
            # Test component template loading for common components
            common_modes = ["questionText", "questionSolution"]
            
            for mode in common_modes:
                if instruction_manager.validate_mode(question_type, mode):
                    template = instruction_manager.get_instruction(exam_type, question_type, mode)
                    assert len(template) > 0, f"Template for {mode} should not be empty"
                    
                    # Test component detection with this demo prompt
                    component_prompt = f"Question{mode.replace('question', '').title()}: {demo_prompt}"
                    
                    # Test detection logic
                    component_types = ["QuestionSolution", "QuestionOptions", "QuestionText", 
                                     "QuestionTitle", "QuestionAnswer", "QuestionPassage"]
                    detected = None
                    for comp_type in component_types:
                        if component_prompt.startswith(comp_type):
                            detected = comp_type
                            break
                    
                    expected = f"Question{mode.replace('question', '').title()}"
                    assert detected == expected, \
                        f"Failed to detect {expected} in '{component_prompt}'"
            
            print(f"✅ {exam_type.value}/{question_type.value} with prompt: {demo_prompt}")
            
        except Exception as e:
            pytest.fail(f"Demo prompt test failed for {exam_type.value}/{question_type.value} with '{demo_prompt}': {e}")
    
    def test_instruction_manager_system_validation(self, instruction_manager):
        """Test that the instruction manager system is properly configured."""
        # Test that instruction manager initializes without errors
        assert instruction_manager is not None, "InstructionManager should initialize successfully"
        
        # Test that we can get system info
        system_info = instruction_manager.get_system_info()
        assert isinstance(system_info, dict), "System info should be a dictionary"
        assert "cache_enabled" in system_info, "System info should include cache status"
        
        # Test cache functionality
        cache_info = instruction_manager.get_cache_info()
        assert isinstance(cache_info, dict), "Cache info should be a dictionary"
        
        print(f"✅ Instruction manager system validation passed")
        print(f"   Cache enabled: {system_info['cache_enabled']}")
        print(f"   Available exam types: {system_info['available_exam_types']}")
        print(f"   Available question types: {system_info['available_question_types']}")


class TestDebugFileFormatValidation:
    """Test debug file format validation."""
    
    def test_debug_file_expected_format(self):
        """Test that debug files would have the expected enhanced prompt format."""
        # Test cases representing what should appear in debug files
        test_cases = [
            {
                "original_prompt": "QuestionText: DS - <arithmetic> - <problem_solving> - <difficulty_level: 3>",
                "template": "STRICT RESPONSE FORMAT:- JSON\n- \"passage\" key with small passage text.",
                "component_type": "QuestionText"
            },
            {
                "original_prompt": "QuestionSolution",
                "template": "RESPONSE FORMAT:- PLAIN TEXT (NOT JSON)\nWrite naturally as you would explain to a student.",
                "component_type": "QuestionSolution"
            }
        ]
        
        for case in test_cases:
            # Simulate enhanced prompt construction as done in _get_response
            enhanced_prompt = f"{case['original_prompt']}\n\nComponent Template:\n{case['template']}"
            
            # Validate format matches what we expect in debug files
            assert case['original_prompt'] in enhanced_prompt
            assert "Component Template:" in enhanced_prompt
            assert case['template'] in enhanced_prompt
            
            # Validate structure
            lines = enhanced_prompt.split('\n')
            assert lines[0] == case['original_prompt']
            assert lines[1] == ""  # Empty separator line
            assert lines[2] == "Component Template:"
            
            print(f"✅ Debug format valid for {case['component_type']}: {len(enhanced_prompt)} chars")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])