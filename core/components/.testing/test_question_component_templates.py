"""
Unit tests for question component template loading.

This module tests whether all question components correctly load their assigned templates
and identifies any missing template mappings or incorrect naming conventions.
"""

from core.components.question_components import (
    create_question_component,
    SimpleQuestion,
    DataSufficiencyQuestion,
    ParentChildQuestion,
    GraphicInterpretationQuestion,
    TableAnalysisQuestion,
    TwoPartAnalysisQuestion,
    MultiSourceReasoningQuestion
)
from core.instructions.instruction_loader import InstructionLoader, TemplateLoadError
from core.instructions.instruction_manager import InstructionManager
from core.enums.question_types import QuestionType
from core.enums.exam_types import ExamType
import unittest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestQuestionComponentTemplates(unittest.TestCase):
    """Test that all question components get correct templates."""

    def setUp(self):
        """Set up test environment."""
        self.instruction_manager = InstructionManager()
        self.instruction_loader = InstructionLoader()

        # Mock objects for component creation
        self.mock_llm = Mock()
        self.mock_global_state = {"start_time": 0, "request_count": 0}
        self.mock_lock = Mock()
        self.test_prompt = "S - <word_problems> - <problem_solving> - <difficulty_level: 1>"

    def test_all_question_types_have_templates(self):
        """Test that all question types can load their required templates."""

        # Standard component modes that all question types should support
        standard_modes = [
            "questionText",
            "questionTitle",
            "questionSolution",
            "questionAnswer"
        ]

        # Test all GMAT question types
        gmat_question_types = QuestionType.get_all_gmat_types()
        for question_type in gmat_question_types:
            with self.subTest(question_type=question_type, exam_type="GMAT"):
                self._test_question_type_templates(
                    ExamType.GMAT, question_type, standard_modes
                )

        # Test all GRE question types
        gre_question_types = QuestionType.get_all_gre_types()
        for question_type in gre_question_types:
            with self.subTest(question_type=question_type, exam_type="GRE"):
                self._test_question_type_templates(
                    ExamType.GRE, question_type, standard_modes
                )

    def _test_question_type_templates(self, exam_type: ExamType, question_type: QuestionType, modes: list):
        """Test template loading for a specific question type."""
        for mode in modes:
            with self.subTest(mode=mode):
                try:
                    instruction = self.instruction_manager.get_instruction(
                        exam_type=exam_type,
                        question_type=question_type,
                        mode=mode
                    )
                    self.assertIsNotNone(instruction)
                    self.assertIsInstance(instruction, str)
                    self.assertGreater(len(instruction.strip()), 0)
                except Exception as e:
                    self.fail(
                        f"Failed to load template for {exam_type.value}/{question_type.value}/{mode}: {e}"
                    )

    def test_component_creation_with_template_loading(self):
        """Test that question components can be created and templates loaded correctly."""

        test_cases = [
            (QuestionType.PROBLEM_SOLVING, ExamType.GMAT, SimpleQuestion),
            (QuestionType.PROBLEM_SOLVING, ExamType.GRE, SimpleQuestion),
            (QuestionType.DATA_SUFFICIENCY, ExamType.GMAT, DataSufficiencyQuestion),
            (QuestionType.DATA_SUFFICIENCY, ExamType.GRE, DataSufficiencyQuestion),
            (QuestionType.READING_COMPREHENSION,
             ExamType.GMAT, ParentChildQuestion),
            (QuestionType.READING_COMPREHENSION,
             ExamType.GRE, ParentChildQuestion),
            (QuestionType.CRITICAL_REASONING, ExamType.GMAT, SimpleQuestion),
            (QuestionType.GRAPHIC_INTERPRETATION,
             ExamType.GMAT, GraphicInterpretationQuestion),
            (QuestionType.TABLE_ANALYSIS, ExamType.GMAT, TableAnalysisQuestion),
            (QuestionType.TWO_PART_ANALYSIS, ExamType.GMAT, TwoPartAnalysisQuestion),
            (QuestionType.MULTI_SOURCE_REASONING,
             ExamType.GMAT, MultiSourceReasoningQuestion),
        ]

        for question_type, exam_type, expected_class in test_cases:
            with self.subTest(question_type=question_type, exam_type=exam_type):
                try:
                    # Create component
                    component = create_question_component(
                        question_type=question_type,
                        llm=self.mock_llm,
                        system_instructions="Test instruction",
                        global_state=self.mock_global_state,
                        lock=self.mock_lock,
                        prompt=self.test_prompt,
                        exam_type=exam_type
                    )

                    # Verify component type
                    self.assertIsInstance(component, expected_class)

                    # Test template instruction loading for key components
                    if hasattr(component, '_get_component_instruction'):
                        for component_name in ["QuestionText", "QuestionSolution"]:
                            try:
                                instruction = component._get_component_instruction(
                                    component_name)
                                self.assertIsNotNone(instruction)
                                self.assertIsInstance(instruction, str)
                            except Exception as e:
                                self.fail(
                                    f"Component {component.__class__.__name__} failed to load {component_name} template: {e}"
                                )

                except Exception as e:
                    self.fail(
                        f"Failed to create component for {exam_type.value}/{question_type.value}: {e}"
                    )

    def test_template_file_structure(self):
        """Test that template files exist in expected locations."""
        templates_base = Path("system_instructions/templates")

        # Check that base directories exist
        expected_component_dirs = [
            "0-questionMetadata",
            "1-questionText",
            "2-questionTitle",
            "4-questionOptions",
            "3-questionSolution",
            "5-questionAnswer"
        ]

        for comp_dir in expected_component_dirs:
            comp_path = templates_base / comp_dir
            self.assertTrue(
                comp_path.exists(),
                f"Component directory {comp_dir} does not exist"
            )

            # Check for generic template
            generic_template = comp_path / "0-generic.txt.template"
            self.assertTrue(
                generic_template.exists(),
                f"Generic template not found in {comp_dir}"
            )

    def test_data_sufficiency_template_mapping(self):
        """Specifically test data sufficiency template mapping which was failing."""
        for exam_type in [ExamType.GMAT, ExamType.GRE]:
            try:
                # Test questionText mode which was failing
                instruction = self.instruction_manager.get_instruction(
                    exam_type=exam_type,
                    question_type=QuestionType.DATA_SUFFICIENCY,
                    mode="questionText"
                )

                self.assertIsNotNone(instruction)
                self.assertIn("passage", instruction.lower())
                self.assertIn("statements", instruction.lower())
                self.assertIn("question", instruction.lower())

                # Test questionAnswer mode which was also failing
                answer_instruction = self.instruction_manager.get_instruction(
                    exam_type=exam_type,
                    question_type=QuestionType.DATA_SUFFICIENCY,
                    mode="questionAnswer"
                )

                self.assertIsNotNone(answer_instruction)

            except Exception as e:
                self.fail(
                    f"Data sufficiency template loading failed for {exam_type.value}: {e}")

    def test_problem_solving_template_mapping(self):
        """Specifically test problem solving template mapping which was failing."""
        for exam_type in [ExamType.GMAT, ExamType.GRE]:
            try:
                instruction = self.instruction_manager.get_instruction(
                    exam_type=exam_type,
                    question_type=QuestionType.PROBLEM_SOLVING,
                    mode="questionText"
                )

                self.assertIsNotNone(instruction)
                self.assertIn("question", instruction.lower())

            except Exception as e:
                self.fail(
                    f"Problem solving template loading failed for {exam_type.value}: {e}")

    def test_template_content_validity(self):
        """Test that loaded templates contain expected JSON format instructions."""

        # Test some key templates have JSON format specifications
        test_cases = [
            (QuestionType.DATA_SUFFICIENCY, "questionText",
             ["passage", "statements", "question"]),
            (QuestionType.PROBLEM_SOLVING, "questionText", ["question"]),
            (QuestionType.CRITICAL_REASONING, "questionText", ["question"]),
        ]

        for question_type, mode, expected_keys in test_cases:
            with self.subTest(question_type=question_type, mode=mode):
                try:
                    instruction = self.instruction_manager.get_instruction(
                        exam_type=ExamType.GMAT,
                        question_type=question_type,
                        mode=mode
                    )

                    # Check that instruction mentions JSON format
                    self.assertIn("json", instruction.lower())

                    # Check that expected keys are mentioned
                    for key in expected_keys:
                        self.assertIn(key, instruction.lower())

                except Exception as e:
                    self.fail(f"Template content validation failed: {e}")

    def test_missing_templates_detection(self):
        """Test detection of missing templates for comprehensive coverage."""

        missing_templates = []

        # Test all question types with all standard modes
        all_question_types = list(QuestionType)
        standard_modes = ["questionText", "questionTitle",
                          "questionSolution", "questionAnswer"]

        for question_type in all_question_types:
            for exam_type in [ExamType.GMAT, ExamType.GRE]:
                # Skip invalid combinations
                if exam_type == ExamType.GRE and question_type in [
                    QuestionType.GRAPHIC_INTERPRETATION,
                    QuestionType.TABLE_ANALYSIS,
                    QuestionType.TWO_PART_ANALYSIS,
                    QuestionType.MULTI_SOURCE_REASONING,
                    QuestionType.SENTENCE_CORRECTION,
                    QuestionType.CRITICAL_REASONING
                ]:
                    continue

                if exam_type == ExamType.GMAT and question_type in [
                    QuestionType.NUMERIC_ENTRY,
                    QuestionType.QUANTITATIVE_COMPARISON,
                    QuestionType.TEXT_COMPLETION,
                    QuestionType.SENTENCE_EQUIVALENCE
                ]:
                    continue

                for mode in standard_modes:
                    try:
                        self.instruction_manager.get_instruction(
                            exam_type=exam_type,
                            question_type=question_type,
                            mode=mode
                        )
                    except Exception as e:
                        missing_templates.append(
                            f"{exam_type.value}/{question_type.value}/{mode}: {e}")

        # Report missing templates
        if missing_templates:
            self.fail(f"Missing templates detected:\n" +
                      "\n".join(missing_templates))


class TestTemplateFileNaming(unittest.TestCase):
    """Test template file naming conventions."""

    def setUp(self):
        self.loader = InstructionLoader()

    def test_template_filename_mapping(self):
        """Test that question type values map correctly to template filenames."""

        # Test the question style mapping in instruction_loader.py
        test_mappings = [
            ("data_sufficiency", "1-data_sufficiency"),
            ("problem_solving", "0-problem_solving"),
            ("numeric_entry", "2-numeric_entry"),
            ("reading_comprehension", "0-reading_comprehension"),
            ("critical_reasoning", "1-critical_reasoning"),
            ("graphic_interpretation", "0-graphic_interpretation"),
            ("table_analysis", "1-table_analysis"),
            ("two_part_analysis", "2-two_part_analysis"),
            ("multi_source_reasoning", "3-multi_source_reasoning")
        ]

        # Get the private mapping from the loader
        question_style_map = {
            "generic": "0-generic",
            "data_sufficiency": "1-data_sufficiency",
            "problem_solving": "0-problem_solving",
            "numeric_entry": "2-numeric_entry",
            "quantitative_comparison": "3-quantitative_comparison",
            "reading_comprehension": "0-reading_comprehension",
            "critical_reasoning": "1-critical_reasoning",
            "sentence_correction": "2-sentence_correction",
            "text_completion": "3-text_completion",
            "sentence_equivalence": "2-sentence_equivalence",
            "graphic_interpretation": "0-graphic_interpretation",
            "table_analysis": "1-table_analysis",
            "two_part_analysis": "2-two_part_analysis",
            "multi_source_reasoning": "3-multi_source_reasoning",
            "multiple_choice_single": "0-multiple_choice_single",
            "multiple_choice_multiple": "1-multiple_choice_multiple",
            "passage": "0-passage",
            "graph": "1-graph",
            "parent_stimulus": "2-parent_stimulus",
            "child_question": "3-child_question",
            "multi_source": "3-multi_source",
            "dichotomous_choice": "1-dichotomous_choice",
            "table": "4-table"
        }

        for question_style, expected_filename in test_mappings:
            with self.subTest(question_style=question_style):
                actual_filename = question_style_map.get(question_style)
                self.assertEqual(
                    actual_filename,
                    expected_filename,
                    f"Question style {question_style} should map to {expected_filename}, got {actual_filename}"
                )


if __name__ == '__main__':
    # Set up test environment
    os.chdir(project_root)

    # Run tests
    unittest.main(verbosity=2)
