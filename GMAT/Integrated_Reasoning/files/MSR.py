from ctypes import Array
import random
import json
import os
import re
from typing import Dict, Any, Optional

# Import unified components
from click import prompt
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
            pattern = r'MSR - <total_child_questions: \d+> - <([^>]+)> - <([^>]+)> - <([^>]+)> - <([^>]+)> - <([^>]+)> - <([^>]+)> - <difficulty_level: \d+>'
            match = re.search(pattern, self.prompt)
            if not match:
                raise ValueError(
                    f"This is the fucking problem here this prompt: \n{self.prompt}\n it is not having any match ")
            question_theme = match.group(1)
            source_infos = [match.group(2), match.group(3), match.group(4)]
            focused_skills_string = match.group(5)
            question_styles_string = match.group(6)

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
                # Construct a focused prompt for each source
                source_prompt = f"MSR - <{question_theme}> - <{source_type}> - <difficulty_level: {self.extract_difficulty_from_prompt()}>"
                source = msr.generate_SourceInfo(
                    f"SourceInfo_{idx} having {source_type}: {source_prompt}", idx)
                if source is None or not isinstance(source, dict):
                    print(
                        f"Error: Failed to generate source info {idx} for MSR. Got: {type(source)}, Value: {source}")
                    return None

                # Transform to required structure based on customizations.json
                try:
                    transformed_source = {
                        "source_info": source.get("source_info", ""),
                    }
                except AttributeError as e:
                    print(f"Error accessing source.get('source_info'): {e}")
                    print(f"source type: {type(source)}, value: {source}")
                    return None

                # Add the appropriate content based on type from customizations.json
                try:
                    content = source.get("content", {})
                except AttributeError as e:
                    print(f"Error accessing source.get('content'): {e}")
                    print(f"source type: {type(source)}, value: {source}")
                    return None
                    
                try:
                    content_type = content.get("type", source_type.lower())
                except AttributeError as e:
                    print(f"Error accessing content.get('type'): {e}")
                    print(f"content type: {type(content)}, value: {content}")
                    return None

                # Get graph types and table types from customizations.json
                graph_types = self.MSR.get("graph_types", [])
                table_types = self.MSR.get("table_types", [])

                if content_type == "passage" or source_type.lower() == "passage":
                    transformed_source["type"] = "passage"
                    try:
                        transformed_source["passage"] = content.get("text", "")
                    except AttributeError as e:
                        print(f"Error accessing content.get('text') for passage: {e}")
                        print(f"content type: {type(content)}, value: {content}")
                        return None
                elif content_type in graph_types or source_type.lower() in graph_types:
                    transformed_source["type"] = "graphs"
                    transformed_source["graphs"] = [content]
                elif content_type in table_types or source_type.lower() in table_types:
                    transformed_source["type"] = "tables"
                    transformed_source["tables"] = [content]
                else:
                    # Default fallback
                    transformed_source["type"] = content_type
                    transformed_source[content_type] = content

                sources["sources"].append(transformed_source)

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
                    try:
                        options, correct_option = answer_data
                    except (ValueError, TypeError) as e:
                        print(f"Error unpacking answer_data for MCQ: {e}")
                        print(f"answer_data type: {type(answer_data)}, value: {answer_data}")
                        return None
                        
                    try:
                        question["answer"] = options[correct_option] if correct_option in options else list(
                            options.values())[0]
                    except AttributeError as e:
                        print(f"Error accessing options.values() in MCQ: {e}")
                        print(f"options type: {type(options)}, value: {options}")
                        return None
                    except Exception as e:
                        # checking if it is failing here
                        raise ValueError(
                            f"question_style is being {question_style} while correct_option is being: \n{correct_option}")
                    
                    try:
                        options = list(options.values())
                    except AttributeError as e:
                        print(f"Error accessing options.values() for list conversion: {e}")
                        print(f"options type: {type(options)}, value: {options}")
                        return None
                else:
                    # Contains info telling what ChildQuestion type is requested
                    question["answer"] = answer_data
                    try:
                        options = list(answer_data.values()) if isinstance(
                            answer_data, dict) else [str(answer_data)]
                    except AttributeError as e:
                        print(f"Error accessing answer_data.values(): {e}")
                        print(f"answer_data type: {type(answer_data)}, value: {answer_data}")
                        return None

                # Clean up question style and shuffle options
                question_style_clean = re.sub(r' \(.*\)', '', question_style)
                # Only shuffle if options is a list of strings, not dicts
                if all(isinstance(opt, str) for opt in options):
                    random.shuffle(options)
                question["options"] = options
                # Tags for child questions should include focused skill, question style
                question["tags"] = [focused_skill, question_style_clean]
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
