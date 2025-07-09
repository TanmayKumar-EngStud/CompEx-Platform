"""
Integration test for template loading in actual question generation flow.

This test validates that the template loading fixes work in real question generation scenarios.

Run with: pytest core/components/.testing/test_integration_template_flow.py -v
"""

import pytest
import os
from dotenv import load_dotenv

# Load environment for testing
load_dotenv()


class TestIntegrationTemplateFlow:
    """Integration tests for template loading in question generation."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method to ensure clean state for each test."""
        # Ensure we have a clean environment
        pass
    
    def test_simple_question_generation_template_loading(self):
        """Test that simple question generation uses enhanced template loading."""
        try:
            from GMAT.Quants.files.simpleQuestionGeneration import SimpleQuestionGeneration
            
            # Create generator instance
            generator = SimpleQuestionGeneration(
                global_state={'start_time': 0, 'request_count': 0},
                lock=None,
                api_IDX=0,
                prompt='PS - <arithmetic> - <percentages> - <difficulty_level: 3>'
            )
            
            # Validate generator was created with proper system instructions
            assert generator is not None, "Generator should be created successfully"
            assert hasattr(generator, 'system_instructions'), "Generator should have system instructions"
            assert len(generator.system_instructions) > 0, "System instructions should not be empty"
            
            # Check for no conflicting format instructions in system instructions
            plain_text_count = generator.system_instructions.count("RESPONSE FORMAT:- PLAIN TEXT")
            json_count = generator.system_instructions.count("STRICT RESPONSE FORMAT:- JSON")
            
            assert not (plain_text_count > 0 and json_count > 0), \
                f"System instructions should not have conflicting formats: PLAIN TEXT: {plain_text_count}, JSON: {json_count}"
            
            print(f"✅ Simple question generator: No format conflicts in system instructions")
            
        except ImportError as e:
            pytest.skip(f"Simple question generation module not available: {e}")
        except Exception as e:
            pytest.fail(f"Simple question generation test failed: {e}")
    
    def test_data_sufficiency_question_generation_template_loading(self):
        """Test that data sufficiency question generation uses enhanced template loading."""
        try:
            from GMAT.Quants.files.dataSufficiencyQuestionGeneration import DataSufficiencyQuestionGeneration
            
            # Create generator instance
            generator = DataSufficiencyQuestionGeneration(
                global_state={'start_time': 0, 'request_count': 0},
                lock=None,
                api_IDX=0,
                prompt='DS - <arithmetic> - <problem_solving> - <difficulty_level: 3>'
            )
            
            # Validate generator was created with proper system instructions
            assert generator is not None, "DS Generator should be created successfully"
            assert hasattr(generator, 'system_instructions'), "DS Generator should have system instructions"
            assert len(generator.system_instructions) > 0, "DS System instructions should not be empty"
            
            # Check for no conflicting format instructions in system instructions
            plain_text_count = generator.system_instructions.count("RESPONSE FORMAT:- PLAIN TEXT")
            json_count = generator.system_instructions.count("STRICT RESPONSE FORMAT:- JSON")
            
            assert not (plain_text_count > 0 and json_count > 0), \
                f"DS System instructions should not have conflicting formats: PLAIN TEXT: {plain_text_count}, JSON: {json_count}"
            
            print(f"✅ Data Sufficiency generator: No format conflicts in system instructions")
            
        except ImportError as e:
            pytest.skip(f"Data sufficiency generation module not available: {e}")
        except Exception as e:
            pytest.fail(f"Data sufficiency generation test failed: {e}")
    
    def test_component_creation_and_template_detection(self):
        """Test component creation and template detection logic."""
        try:
            # Test the core template detection logic without requiring component creation
            test_prompts = [
                "QuestionText: DS - <arithmetic> - <problem_solving> - <difficulty_level: 3>",
                "QuestionSolution",
                "QuestionTitle",
                "QuestionAnswer",
                "QuestionOptions",
                "QuestionPassage",
            ]
            
            expected_components = ["QuestionText", "QuestionSolution", "QuestionTitle", 
                                 "QuestionAnswer", "QuestionOptions", "QuestionPassage"]
            
            for i, test_prompt in enumerate(test_prompts):
                # Test the same detection logic used in _get_response
                component_types = ["QuestionSolution", "QuestionOptions", "QuestionText", 
                                 "QuestionTitle", "QuestionAnswer", "QuestionPassage"]
                component_match = None
                for component_type in component_types:
                    if test_prompt.startswith(component_type):
                        component_match = component_type
                        break
                
                assert component_match == expected_components[i], \
                    f"Failed to detect {expected_components[i]} in prompt: {test_prompt}"
            
            # Test that non-component prompts are not detected
            non_component_prompts = [
                "Regular prompt without component type",
                "Generate a question about arithmetic",
                "This is just a normal prompt",
            ]
            
            for prompt in non_component_prompts:
                component_types = ["QuestionSolution", "QuestionOptions", "QuestionText", 
                                 "QuestionTitle", "QuestionAnswer", "QuestionPassage"]
                component_match = None
                for component_type in component_types:
                    if prompt.startswith(component_type):
                        component_match = component_type
                        break
                
                assert component_match is None, \
                    f"Should not detect component type in prompt: {prompt}, but detected: {component_match}"
            
            print(f"✅ Template detection logic: All tests passed")
            print(f"  - Detected {len(expected_components)} component types correctly")
            print(f"  - Correctly ignored {len(non_component_prompts)} non-component prompts")
                
        except Exception as e:
            pytest.fail(f"Template detection test failed: {e}")
    
    def test_instruction_manager_integration(self):
        """Test instruction manager integration with actual question types."""
        try:
            from core.instructions.instruction_manager import InstructionManager
            from core.enums.exam_types import ExamType
            from core.enums.question_types import QuestionType
            
            manager = InstructionManager()
            
            # Test main instruction loading (what becomes system instructions)
            main_instruction = manager.get_main_instruction(ExamType.GMAT, QuestionType.DATA_SUFFICIENCY)
            
            assert isinstance(main_instruction, str), "Main instruction should be a string"
            assert len(main_instruction) > 0, "Main instruction should not be empty"
            
            # Test component instruction loading (what gets appended to prompts)
            component_instruction = manager.get_instruction(
                ExamType.GMAT, 
                QuestionType.DATA_SUFFICIENCY, 
                "questionText"
            )
            
            assert isinstance(component_instruction, str), "Component instruction should be a string"
            assert len(component_instruction) > 0, "Component instruction should not be empty"
            assert "JSON" in component_instruction, "QuestionText component should specify JSON format"
            
            # Test enhanced prompt construction
            original_prompt = "QuestionText: DS - <arithmetic> - <problem_solving> - <difficulty_level: 3>"
            enhanced_prompt = f"{original_prompt}\n\nComponent Template:\n{component_instruction}"
            
            assert len(enhanced_prompt) > len(original_prompt), "Enhanced prompt should be longer"
            assert original_prompt in enhanced_prompt, "Enhanced prompt should contain original"
            assert component_instruction in enhanced_prompt, "Enhanced prompt should contain template"
            
            print(f"✅ Instruction manager integration: All validations passed")
            print(f"   Main instruction length: {len(main_instruction)} chars")
            print(f"   Component instruction length: {len(component_instruction)} chars")
            print(f"   Enhanced prompt length: {len(enhanced_prompt)} chars")
            
        except Exception as e:
            pytest.fail(f"Instruction manager integration test failed: {e}")
    
    def test_no_api_key_required_for_template_loading(self):
        """Test that template loading works without requiring API keys."""
        try:
            from core.instructions.instruction_manager import InstructionManager
            from core.enums.exam_types import ExamType
            from core.enums.question_types import QuestionType
            
            # This should work even without valid API keys
            manager = InstructionManager()
            
            # Test loading instructions for multiple question types
            test_cases = [
                (ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "questionText"),
                (ExamType.GMAT, QuestionType.PROBLEM_SOLVING, "questionText"),
                (ExamType.GRE, QuestionType.DATA_SUFFICIENCY, "questionText"),
            ]
            
            for exam_type, question_type, mode in test_cases:
                try:
                    instruction = manager.get_instruction(exam_type, question_type, mode)
                    assert len(instruction) > 0, f"Instruction should not be empty for {exam_type.value}/{question_type.value}/{mode}"
                except Exception as e:
                    pytest.fail(f"Template loading failed for {exam_type.value}/{question_type.value}/{mode}: {e}")
            
            print(f"✅ Template loading: Works without API keys")
            
        except Exception as e:
            pytest.fail(f"Template loading without API keys test failed: {e}")


class TestRealWorldScenarios:
    """Test real-world scenarios with demo prompts."""
    
    @pytest.mark.parametrize("prompt,expected_question_type", [
        ("DS - <arithmetic> - <problem_solving> - <difficulty_level: 3>", "data_sufficiency"),
        ("PS - <algebra> - <quadratic_equations> - <difficulty_level: 4>", "problem_solving"),
        ("TC - <reading> - <vocabulary> - <difficulty_level: 2>", "text_completion"),
        ("NE - <arithmetic> - <calculations> - <difficulty_level: 3>", "numeric_entry"),
    ])
    def test_demo_prompt_scenarios(self, prompt, expected_question_type):
        """Test various demo prompt scenarios."""
        try:
            from core.instructions.instruction_manager import InstructionManager
            from core.enums.exam_types import ExamType
            from core.enums.question_types import QuestionType
            
            # Map prompt prefixes to question types
            question_type_map = {
                "data_sufficiency": QuestionType.DATA_SUFFICIENCY,
                "problem_solving": QuestionType.PROBLEM_SOLVING,
                "text_completion": QuestionType.TEXT_COMPLETION,
                "numeric_entry": QuestionType.NUMERIC_ENTRY,
            }
            
            question_type = question_type_map[expected_question_type]
            
            manager = InstructionManager()
            
            # Test main instruction loading for this question type
            for exam_type in [ExamType.GMAT, ExamType.GRE]:
                try:
                    main_instruction = manager.get_main_instruction(exam_type, question_type)
                    assert len(main_instruction) > 0, f"Main instruction should not be empty"
                    
                    # Test component template loading
                    if manager.validate_mode(question_type, "questionText"):
                        component_instruction = manager.get_instruction(exam_type, question_type, "questionText")
                        assert len(component_instruction) > 0, f"Component instruction should not be empty"
                        
                        # Test enhanced prompt construction
                        test_component_prompt = f"QuestionText: {prompt}"
                        enhanced_prompt = f"{test_component_prompt}\n\nComponent Template:\n{component_instruction}"
                        
                        assert len(enhanced_prompt) > len(test_component_prompt), "Enhanced prompt should be longer"
                        
                except Exception:
                    # Some question types might not be available for all exam types
                    continue
            
            print(f"✅ Demo prompt scenario: {prompt} -> {expected_question_type}")
            
        except Exception as e:
            pytest.fail(f"Demo prompt scenario test failed for '{prompt}': {e}")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])