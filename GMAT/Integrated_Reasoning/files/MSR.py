from ctypes import Array
import random
import json
import os
import re
from typing import Dict, Any, Optional

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter


class Generate_MSR(BaseQuestionGenerator):
    """GMAT Multi-Source Reasoning Question Generator using unified architecture."""

    def __init__(self, global_state, lock, api_IDX, prompt):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GMAT,
            question_type=QuestionType.MULTI_SOURCE_REASONING,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )

        # MSR-specific initialization
        search = re.search(r"total_child_questions: (\d+)", self.prompt)
        self.total_child_questions = 3
        if search:
            self.total_child_questions = int(search.group(1))

        try:
            self.MSR = json.load(
                open(os.path.join(os.path.dirname(__file__), "../../../system_instructions/gmat/customizations.json")))["integrated reasoning"]["multi source reasoning"]
        except FileNotFoundError:
            print("MSR combinations file not found, using default values")
            self.MSR = {}

    def generate_question(self) -> Optional[Dict[str, Any]]:
        """
        Generate a GMAT Multi-Source Reasoning question.

        Returns:
            Generated question data or None if generation fails
        """
        try:
            # Initialize question data using base class
            self.initialize_question_data(self.prompt)

            # Create unified component and wrap with GMAT adapter
            component = create_question_component(
                question_type=QuestionType.MULTI_SOURCE_REASONING,
                llm=self.llm,
                system_instructions=self.system_instructions,
                global_state=self.global_state,
                lock=self.lock,
                prompt=self.prompt,
                exam_type=ExamType.GMAT
            )
            # Parse source_infos, focused_skills, and question_style from the prompt generated in Integrated_Reasoning.py
            # Extract source types from the structured prompt
            import re
            # "nomenclature": "MSR - <total_child_questions: {3}> <questionTheme> - <source_info1> - <source_info2> - <source_info3> - <focused_skill_1/focused_skill_2/focused_skill_3> - <question_style_1/question_style_2/question_style_3> - <difficulty_level: {1-5}>",
            pattern = r'MSR - <total_child_questions: \d+> - <[^>]+> - <([^>]+)> - <([^>]+)> - <([^>]+)> - <([^>]+)> - <([^>]+)> - <difficulty_level: \d+>'
            match = re.search(pattern, self.prompt)

            if match:
                source_infos = [match.group(1), match.group(2), match.group(3)]
                focused_skills_string = match.group(4)
                question_styles_string = match.group(5)

                # Parse focused skills and question styles separated by '/'
                focused_skills_from_prompt = focused_skills_string.split('/')
                question_styles_from_prompt = question_styles_string.split('/')

                # Ensure we have enough skills and styles for all child questions
                while len(focused_skills_from_prompt) < self.total_child_questions:
                    focused_skills_from_prompt.extend(
                        focused_skills_from_prompt)
                focused_skills_from_prompt = focused_skills_from_prompt[:self.total_child_questions]

                while len(question_styles_from_prompt) < self.total_child_questions:
                    question_styles_from_prompt.extend(
                        question_styles_from_prompt)
                question_styles_from_prompt = question_styles_from_prompt[:self.total_child_questions]
            else:
                # Fallback to default if parsing fails
                source_infos = []
                for _ in range(3):
                    source_infos.append(random.choice(
                        self.MSR.get("source_info", ["Passage"])))
                focused_skills_from_prompt = [
                    "Critical Reasoning"] * self.total_child_questions
                question_styles_from_prompt = [
                    "MCQ (5 options MCQ)"] * self.total_child_questions

            msr = GMATAdapter.adapt_multi_source_reasoning(
                self.prompt, component)

            # Load combinations data
            sources = {"sources": []}

            # Generate sources
            for idx in range(1, 4):
                # "nomenclature": "MSR Source_info{i} - <source_info>"
                # Fix: 0-indexed array but 1-indexed loop
                source_type = source_infos[idx-1]
                # Format: "SourceInfo_1 having Line Chart: MSR - <Business> - <Data Interpretation> - <difficulty_level: 2>"
                source = msr.generate_SourceInfo(
                    f"SourceInfo_{idx} having {source_type}: {self.prompt}", idx)
                sources["sources"].append(source)

            self.question_data["content"] = sources
            self.question_data["title"] = msr.generate_MainQuestionTitle()
            self.question_data["questions"] = []

            collective_tags = set()

            # Generate child questions
            for idx in range(1, self.total_child_questions + 1):
                question = {}
                focused_skill = focused_skills_from_prompt[idx-1]
                question_style = question_styles_from_prompt[idx-1]

                # Set difficulty level with variation logic
                main_difficulty = self.extract_difficulty_from_prompt()
                if main_difficulty == 1:
                    difficulty_level = random.choice([1, 2])
                elif main_difficulty == 5:
                    difficulty_level = random.choice([4, 5])
                else:
                    difficulty_level = random.choice(
                        [main_difficulty-1, main_difficulty, main_difficulty+1])

                question["type"] = question_style
                question["prompt"] = f"<{focused_skill}> - <{question_style}> - <{difficulty_level}>"
                question["question"] = msr.generate_QuestionText(
                    question["prompt"], idx)
                question["title"] = msr.generate_QuestionTitle()
                question["solution"] = msr.generate_QuestionSolution()
                answer_data = msr.generate_QuestionOptions(question_style)
                # Generate options and answers
                if question_style == "MCQ (5 options MCQ)":
                    options, correct_option = answer_data
                    question["answer"] = options[correct_option] if correct_option in options else list(
                        options.values())[0]
                    options = list(options.values())
                else:

                    # Contains info telling what ChildQuestion type is requested
                    question["answer"] = answer_data
                    options = list(answer_data.values()) if isinstance(
                        answer_data, dict) else [str(answer_data)]

                # Clean up question style and shuffle options
                question_style_clean = re.sub(r' \(.*?\)', '', question_style)
                random.shuffle(options)
                question["options"] = options
                question["tags"] = [focused_skill,
                                    question_style_clean, "MSR", source_type]
                collective_tags.update(question["tags"])
                question["difficulty"] = difficulty_level
                self.question_data["questions"].append(question)

            self.question_data["tags"] = list(collective_tags)

            return self.question_data

        except Exception as e:
            print(
                f"Error generating GMAT Multi-Source Reasoning question: {e}")
            return None

    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GMAT Multi-Source Reasoning question format.

        Args:
            question_data: Generated question data to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["type", "content", "questions", "title"]

        # Check required fields
        for field in required_fields:
            if field not in question_data:
                return False

        # Validate content structure
        content = question_data.get("content", {})
        if not isinstance(content, dict) or "sources" not in content:
            return False

        sources = content.get("sources", [])
        if not isinstance(sources, list) or len(sources) != 3:
            return False

        # Validate questions array
        questions = question_data.get("questions", [])
        if not isinstance(questions, list) or len(questions) == 0:
            return False

        # Validate each child question
        for question in questions:
            if not isinstance(question, dict):
                return False
            required_question_fields = [
                "type", "question", "options", "answer"]
            for field in required_question_fields:
                if field not in question:
                    return False

        return True

    def get_supported_types(self) -> list[QuestionType]:
        """Get supported question types."""
        return [QuestionType.MULTI_SOURCE_REASONING]

    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GMAT


# g = Generate_MSR("<MSR> - <total_child_questions: 3> - <Business> - <difficulty_level: 4>")
# content = g.generate_MSR()
# json.dump(content, open(os.path.join(os.path.dirname(__file__), "MSR-component.json"), "w"))
