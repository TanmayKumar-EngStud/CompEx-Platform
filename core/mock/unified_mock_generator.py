"""
Unified Mock Generator for GMAT and GRE Exams.

This module provides a unified interface for generating mock exam papers for both GMAT and GRE.
It eliminates code duplication by using a strategy pattern with exam-specific configurations.
"""

import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

# Core imports
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.threading import APIThreadPoolManager, ThreadConfig
from core.threading.thread_config import PaperStructure
from core.factories.question_generator_factory import get_question_generator_factory
from core.utilities.logging_utils import StructuredLogger

# Configuration imports - will create simplified configs for now
from config.exams.base_exam_config import BaseExamConfig
from config.exams.gmat_config import GMATConfig
from config.exams.gre_config import GREConfig


class GeneratorClass(Enum):
    """Legacy generator class enum for backward compatibility."""
    # GMAT generators
    Q_DS_gen = "Q_DS_gen"
    Q_S_gen = "Q_S_gen"
    V_PC_gen = "V_PC_gen"
    V_S_gen = "V_S_gen"
    GI_gen = "GI_gen"
    TPA_gen = "TPA_gen"
    TA_gen = "TA_gen"
    MSR_gen = "MSR_gen"

    # GRE generators
    Q_PC_gen = "Q_PC_gen"
    Q_NE_gen = "Q_NE_gen"


class UnifiedMockGenerator:
    """
    Unified mock generator for both GMAT and GRE exams.

    This class provides a common interface for generating mock papers while handling
    exam-specific differences through configuration and strategy patterns.

    Attributes:
        exam_type: The type of exam (GMAT or GRE)
        mock_difficulty: Overall difficulty level of the mock exam
        config: Exam-specific configuration
        max_retries: Maximum number of retries for question generation

    Example:
        >>> generator = UnifiedMockGenerator(ExamType.GMAT, 3)
        >>> paper = generator.generate_mock_paper()
    """

    def __init__(self, exam_type: ExamType, mock_difficulty: int) -> None:
        """
        Initialize the unified mock generator.

        Args:
            exam_type: The exam type (GMAT or GRE)
            mock_difficulty: Difficulty level for the mock exam (1-5)
        """
        self.exam_type = exam_type
        self.mock_difficulty = mock_difficulty
        self.max_retries = 3
        self.logger = StructuredLogger(
            f"UnifiedMockGenerator_{exam_type.value}", level="ERROR")

        # Load exam-specific configuration
        self.config = self._load_exam_config()

        # Initialize prompts using simplified approach for now
        self.prompts = self._initialize_prompts_simple()

        # Legacy generator mappings for backward compatibility
        self.legacy_mappings = self._get_legacy_mappings()

    def _load_exam_config(self) -> BaseExamConfig:
        """Load exam-specific configuration."""
        if self.exam_type == ExamType.GMAT:
            return GMATConfig.from_difficulty(self.mock_difficulty)
        elif self.exam_type == ExamType.GRE:
            return GREConfig.from_difficulty(self.mock_difficulty)
        else:
            raise ValueError(f"Unsupported exam type: {self.exam_type}")

    def _initialize_prompts_simple(self) -> Dict[str, List[str]]:
        """Initialize section prompts using simplified approach."""
        prompts = {}

        if self.exam_type == ExamType.GMAT:
            # Generate basic GMAT prompts
            prompts["quantitative"] = self._generate_gmat_quant_prompts()
            prompts["verbal"] = self._generate_gmat_verbal_prompts()
            prompts["integrated_reasoning"] = self._generate_gmat_ir_prompts()
        elif self.exam_type == ExamType.GRE:
            # Generate basic GRE prompts
            prompts["quantitative"] = self._generate_gre_quant_prompts()
            prompts["verbal"] = self._generate_gre_verbal_prompts()

        return prompts

    def _generate_gmat_quant_prompts(self) -> List[str]:
        """Generate GMAT quantitative prompts."""
        prompts = []
        topics = ["arithmetic", "algebra", "geometry", "word_problems"]
        styles = ["DS", "S"]

        for i in range(21):  # 21 base questions
            style = styles[i % len(styles)]
            topic = topics[i % len(topics)]
            difficulty = min(5, max(1, self.mock_difficulty + (i % 3 - 1)))
            prompts.append(
                f"{style} - <{topic}> - <problem_solving> - <difficulty_level: {difficulty}>")

        return prompts

    def _generate_gmat_verbal_prompts(self) -> List[str]:
        """Generate GMAT verbal prompts."""
        prompts = []
        themes = ["business", "science", "history", "literature"]

        # RC prompts
        for i in range(13):
            theme = themes[i % len(themes)]
            difficulty = min(5, max(1, self.mock_difficulty + (i % 3 - 1)))
            prompts.append(
                f"RC_3 - <{theme}> - <reading_comprehension> - <difficulty_level: {difficulty}>")

        # CR prompts
        cr_types = ["strengthen", "weaken", "assumption", "inference"]
        for i in range(10):
            cr_type = cr_types[i % len(cr_types)]
            difficulty = min(5, max(1, self.mock_difficulty + (i % 3 - 1)))
            prompts.append(
                f"CR - <critical_reasoning> - <{cr_type}> - <difficulty_level: {difficulty}>")

        return prompts

    def _generate_gmat_ir_prompts(self) -> List[str]:
        """Generate GMAT IR prompts."""
        prompts = []
        ir_types = ["GI", "TPA", "TA", "MSR"]
        topics = ["Economics", "Business", "Science"]

        for i in range(8):
            ir_type = ir_types[i % len(ir_types)]
            topic = topics[i % len(topics)]
            difficulty = min(5, max(1, self.mock_difficulty + (i % 3 - 1)))
            prompts.append(
                f"{ir_type} - <{topic}> - <Data Interpretation> - <difficulty_level: {difficulty}>")

        return prompts

    def _generate_gre_quant_prompts(self) -> List[str]:
        """Generate GRE quantitative prompts."""
        prompts = []
        topics = ["arithmetic", "algebra", "geometry", "data_analysis"]
        styles = ["S", "DS", "NE", "PC"]

        for i in range(15):  # 15 questions per section
            style = styles[i % len(styles)]
            topic = topics[i % len(topics)]
            difficulty = min(5, max(1, self.mock_difficulty + (i % 3 - 1)))
            prompts.append(
                f"{style} - <{topic}> - <problem_solving> - <difficulty_level: {difficulty}>")

        return prompts

    def _generate_gre_verbal_prompts(self) -> List[str]:
        """Generate GRE verbal prompts."""
        prompts = []
        themes = ["science", "humanities", "social_sciences", "literature"]

        # RC prompts
        for i in range(4):
            theme = themes[i % len(themes)]
            difficulty = min(5, max(1, self.mock_difficulty + (i % 3 - 1)))
            prompts.append(
                f"RC_S - <{theme}> - <reading_comprehension> - <difficulty_level: {difficulty}>")

        # TC prompts
        for i in range(6):
            difficulty = min(5, max(1, self.mock_difficulty + (i % 3 - 1)))
            prompts.append(
                f"TC_1 - <academic> - <text_completion> - <difficulty_level: {difficulty}>")

        # SE prompts
        for i in range(5):
            difficulty = min(5, max(1, self.mock_difficulty + (i % 3 - 1)))
            prompts.append(
                f"SE - <vocabulary> - <sentence_equivalence> - <difficulty_level: {difficulty}>")

        return prompts

    def _get_legacy_mappings(self) -> Dict[GeneratorClass, Tuple[QuestionType, SectionType]]:
        """Get legacy generator mappings for backward compatibility."""
        if self.exam_type == ExamType.GMAT:
            return {
                GeneratorClass.Q_DS_gen: (QuestionType.DATA_SUFFICIENCY, SectionType.QUANTITATIVE),
                GeneratorClass.Q_S_gen: (QuestionType.PROBLEM_SOLVING, SectionType.QUANTITATIVE),
                GeneratorClass.V_PC_gen: (QuestionType.READING_COMPREHENSION, SectionType.VERBAL),
                GeneratorClass.V_S_gen: (QuestionType.CRITICAL_REASONING, SectionType.VERBAL),
                GeneratorClass.GI_gen: (QuestionType.GRAPHIC_INTERPRETATION, SectionType.INTEGRATED_REASONING),
                GeneratorClass.TPA_gen: (QuestionType.TWO_PART_ANALYSIS, SectionType.INTEGRATED_REASONING),
                GeneratorClass.TA_gen: (QuestionType.TABLE_ANALYSIS, SectionType.INTEGRATED_REASONING),
                GeneratorClass.MSR_gen: (QuestionType.MULTI_SOURCE_REASONING, SectionType.INTEGRATED_REASONING),
            }
        elif self.exam_type == ExamType.GRE:
            return {
                GeneratorClass.Q_PC_gen: (QuestionType.READING_COMPREHENSION, SectionType.QUANTITATIVE),
                GeneratorClass.Q_DS_gen: (QuestionType.DATA_SUFFICIENCY, SectionType.QUANTITATIVE),
                GeneratorClass.Q_NE_gen: (QuestionType.NUMERIC_ENTRY, SectionType.QUANTITATIVE),
                GeneratorClass.Q_S_gen: (QuestionType.PROBLEM_SOLVING, SectionType.QUANTITATIVE),
                GeneratorClass.V_PC_gen: (QuestionType.READING_COMPREHENSION, SectionType.VERBAL),
                GeneratorClass.V_S_gen: (QuestionType.TEXT_COMPLETION, SectionType.VERBAL),
            }
        else:
            return {}

    def generate_question_with_retry(
        self,
        api_state,
        lock,
        exam_section: str,
        prompt: str,
        generator_class: GeneratorClass,
        api_itr: int,
        section_id: Optional[int] = None
    ) -> List[Any]:
        """
        Generate question with enhanced retry logic for rate limiting and JSON format issues.

        Args:
            api_state: APIState object or dict containing API state information
            lock: Threading lock for this API instance
            exam_section: Section name for the question
            prompt: Generation prompt
            generator_class: Generator class enum
            api_itr: API iterator/index
            section_id: Section ID number (GRE only)

        Returns:
            List containing generation results and metadata
        """
        retries = 0
        json_format_retries = 0
        max_json_retries = 3

        if not isinstance(generator_class, GeneratorClass):
            raise ValueError(f"Invalid generator class: {generator_class}")

        # Get question and section types from legacy mapping
        if generator_class not in self.legacy_mappings:
            raise ValueError(f"Unknown generator class: {generator_class}")

        question_type, section_type = self.legacy_mappings[generator_class]

        # Handle both APIState objects and legacy dict format
        if hasattr(api_state, 'to_dict'):
            global_state = api_state.to_dict()
        else:
            global_state = api_state

        # Get factory instance
        factory = get_question_generator_factory()

        self.logger.log_generation_start(prompt, self.exam_type)

        while retries < self.max_retries:
            try:
                # Create generator using factory
                question_generator = factory.create_generator(
                    exam_type=self.exam_type,
                    question_type=question_type,
                    section_type=section_type,
                    global_state=global_state,
                    lock=lock,
                    api_idx=api_itr,
                    prompt=prompt
                )

                if question_generator is None:
                    raise ValueError(
                        f"Factory failed to create generator for {generator_class}")

                # Generate the question
                question_response = question_generator.generate_question(
                    prompt)

                if question_response:
                    self.logger.log_generation_success(question_response)

                    # Return format varies by exam type
                    if self.exam_type == ExamType.GRE and section_id is not None:
                        return [api_itr, time.time(), 1, exam_section, section_id, question_response]
                    else:
                        return [api_itr, time.time(), 1, exam_section, question_response]
                else:
                    raise ValueError("Generator returned empty response")

            except Exception as e:
                error_str = str(e).lower()

                # Handle rate limiting specifically
                if "rate limit" in error_str or "quota" in error_str or "429" in error_str:
                    print(
                        f"Rate limit hit for API {api_itr}. Waiting 60 seconds before retry...")
                    time.sleep(60)
                    retries += 1
                    continue

                # Handle JSON format issues
                elif ("json" in error_str or "format" in error_str or "parse" in error_str) and json_format_retries < max_json_retries:
                    json_format_retries += 1
                    print(
                        f"JSON format issue detected. Retry attempt {json_format_retries}/{max_json_retries} for refining JSON format...")

                    # Progressive JSON refinement strategy
                    if json_format_retries == 1:
                        # First attempt: Add basic JSON formatting instructions
                        refined_prompt = f"{prompt}\n\nIMPORTANT: Please ensure the response is in valid JSON format with proper escaping of quotes and special characters."
                    elif json_format_retries == 2:
                        # Second attempt: Request simplified JSON with specific guidelines
                        simplified_template = self._get_simplified_json_template(
                            generator_class)
                        refined_prompt = f"{prompt}\n\nIMPORTANT: Due to JSON parsing issues, please provide a simplified response using this exact JSON structure:\n{simplified_template}\n\nEnsure all text is simple and readable without complex formatting or special characters."
                    else:
                        # Final attempt: Request ultra-simple JSON
                        ultra_simple_template = self._get_ultra_simple_json_template(
                            generator_class)
                        refined_prompt = f"{prompt}\n\nCRITICAL: Please provide an ULTRA-SIMPLIFIED response using this exact structure:\n{ultra_simple_template}\n\nRules:\n- Use only simple words\n- No special characters except basic punctuation\n- Keep all text short and clear\n- Use only double quotes for JSON strings\n- No nested complex structures"

                    try:
                        # Retry with refined prompt
                        question_generator = factory.create_generator(
                            exam_type=self.exam_type,
                            question_type=question_type,
                            section_type=section_type,
                            global_state=global_state,
                            lock=lock,
                            api_idx=api_itr,
                            prompt=refined_prompt
                        )

                        question_response = question_generator.generate_question(
                            refined_prompt)

                        if question_response:
                            self.logger.log_generation_success(
                                question_response)
                            # print(f"✅ JSON format retry {json_format_retries} succeeded with {'simplified' if json_format_retries >= 2 else 'refined'} format")

                            if self.exam_type == ExamType.GRE and section_id is not None:
                                return [api_itr, time.time(), json_format_retries, exam_section, section_id, question_response]
                            else:
                                return [api_itr, time.time(), json_format_retries, exam_section, question_response]
                    except Exception as json_retry_error:
                        print(
                            f"❌ JSON refinement retry {json_format_retries} failed: {json_retry_error}")
                        if json_format_retries >= max_json_retries:
                            print(
                                f"🔄 All JSON format retries exhausted. Moving to general retry logic...")
                        time.sleep(2)  # Short wait before next attempt
                        continue

                # Handle other errors
                else:
                    retries += 1
                    print(
                        f"Generation error (attempt {retries}/{self.max_retries}): {e}")

                    if retries >= self.max_retries:
                        # Log final failure and raise exception instead of returning error
                        self.logger.log_generation_error(e, {
                            "retry_attempt": retries,
                            "json_format_retries": json_format_retries,
                            "generator_class": generator_class.value,
                            "exam_section": exam_section,
                            "api_itr": api_itr,
                            "final_failure": True
                        })

                        # Raise the exception instead of returning error response
                        raise RuntimeError(
                            f"Failed to generate question after {retries} retries and {json_format_retries} JSON format retries. Last error: {e}")

                    # Progressive wait time based on retry count
                    # Exponential backoff capped at 10 seconds
                    wait_time = min(10, 2 ** retries)
                    print(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)

    def generate_mock_paper(self) -> Dict[str, Any]:
        """
        Generate a complete mock exam paper using Gemini API for fresh questions.

        Returns:
            Dictionary containing the generated mock paper in the expected database format
        """
        start_time = time.time()

        self.logger.log_generation_start(
            "Mock Paper Generation", self.exam_type)

        try:
            # Create thread configuration based on exam type
            if self.exam_type == ExamType.GMAT:
                config = ThreadConfig.create_gmat_config(max_workers=8)
            else:
                config = ThreadConfig.create_gre_config(max_workers=8)

            # Generate actual questions using API
            thread_manager = APIThreadPoolManager(config)
            paper = self._generate_actual_paper(thread_manager)

            self.logger.log_generation_success({
                "paper_type": "mock_exam_api_generated",
                "exam_type": self.exam_type.value,
                "difficulty": self.mock_difficulty,
                "generation_time": time.time() - start_time,
                "total_questions": self._count_total_questions(paper)
            })

            return paper

        except Exception as e:
            self.logger.log_generation_error(e, {
                "operation": "mock_paper_generation",
                "exam_type": self.exam_type.value,
                "difficulty": self.mock_difficulty
            })

            # Re-raise the exception instead of falling back to samples
            raise

    def _generate_actual_paper(self, thread_manager: APIThreadPoolManager) -> Dict[str, Any]:
        """Generate actual questions using the thread manager and factory system."""

        try:
            # Add tasks to the thread manager
            if self.exam_type == ExamType.GRE:
                self._add_gre_generation_tasks(thread_manager)
            elif self.exam_type == ExamType.GMAT:
                self._add_gmat_generation_tasks(thread_manager)

            # Execute all tasks and get the paper results
            # The thread manager returns the properly structured paper dictionary
            paper = thread_manager.execute_all()

            # If the paper is empty or invalid, return the initial structure
            if not paper or not isinstance(paper, dict):
                # Create empty structure based on exam type
                if self.exam_type == ExamType.GRE:
                    paper = {"GRE_Q": {"section1": [], "section2": []}, "GRE_V": {"section1": [], "section2": []}}
                else:
                    paper = {"GMAT_Q": {"section0": []}, "GMAT_V": {"section0": []}, "GMAT_IR": {"section0": []}}

            return paper

        finally:
            # Ensure thread manager cleanup
            thread_manager.shutdown()

    def _add_gre_generation_tasks(self, thread_manager: APIThreadPoolManager) -> None:
        """Add GRE question generation tasks to the thread manager."""

        # Quantitative section tasks
        for i, prompt in enumerate(self.prompts.get("quantitative", [])):
            generator_class = self._get_generator_class_for_prompt(
                prompt, SectionType.QUANTITATIVE)

            # Add task for section 1
            def task_factory_1():
                return self._create_question_task_factory(
                    'GRE_Q', 1, prompt, generator_class, i)
            thread_manager.add_task(task_factory_1)

            # Add task for section 2 (duplicate for GRE)
            def task_factory_2():
                return self._create_question_task_factory(
                    'GRE_Q', 2, prompt, generator_class, i)
            thread_manager.add_task(task_factory_2)

        # Verbal section tasks
        for i, prompt in enumerate(self.prompts.get("verbal", [])):
            generator_class = self._get_generator_class_for_prompt(
                prompt, SectionType.VERBAL)

            # Add task for section 1
            def task_factory_v1():
                return self._create_question_task_factory(
                    'GRE_V', 1, prompt, generator_class, i)
            thread_manager.add_task(task_factory_v1)

            # Add task for section 2
            def task_factory_v2():
                return self._create_question_task_factory(
                    'GRE_V', 2, prompt, generator_class, i)
            thread_manager.add_task(task_factory_v2)

    def _add_gmat_generation_tasks(self, thread_manager: APIThreadPoolManager) -> None:
        """Add GMAT question generation tasks to the thread manager."""

        # Quantitative section tasks
        for i, prompt in enumerate(self.prompts.get("quantitative", [])):
            generator_class = self._get_generator_class_for_prompt(
                prompt, SectionType.QUANTITATIVE)
            def task_factory_q():
                return self._create_question_task_factory(
                    'GMAT_Q', 0, prompt, generator_class, i)
            thread_manager.add_task(task_factory_q)

        # Verbal section tasks
        for i, prompt in enumerate(self.prompts.get("verbal", [])):
            generator_class = self._get_generator_class_for_prompt(
                prompt, SectionType.VERBAL)
            def task_factory_v():
                return self._create_question_task_factory(
                    'GMAT_V', 0, prompt, generator_class, i)
            thread_manager.add_task(task_factory_v)

        # Integrated Reasoning section tasks
        for i, prompt in enumerate(self.prompts.get("integrated_reasoning", [])):
            generator_class = self._get_generator_class_for_prompt(
                prompt, SectionType.INTEGRATED_REASONING)
            def task_factory_ir():
                return self._create_question_task_factory(
                    'GMAT_IR', 0, prompt, generator_class, i)
            thread_manager.add_task(task_factory_ir)

    def _create_question_task_factory(self, section: str, section_id: int, prompt: str, generator_class: GeneratorClass, question_index: int):
        """Factory function to create question generation tasks."""
        def task_function(api_state, lock, api_itr):
            return self.generate_question_with_retry(
                api_state, lock, section, prompt, generator_class, api_itr, section_id
            )
        return task_function

    def _transform_to_database_format(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """Transform the thread manager paper format to database format."""
        # The thread manager should already organize results properly
        if not paper or not isinstance(paper, dict):
            raise ValueError(
                "Question generation failed - no valid questions were generated")

        return paper

    def _organize_results_into_paper(self, results: List[Any]) -> Dict[str, Any]:
        """Organize generation results into proper paper structure."""
        paper = {}

        for result in results:
            if len(result) >= 5:
                # Extract data from result
                api_itr = result[0]
                start_time = result[1]
                request_count = result[2]
                section = result[3]

                if self.exam_type == ExamType.GRE and len(result) >= 6:
                    section_id = result[4]
                    question_data = result[5]
                else:
                    section_id = 0 if self.exam_type == ExamType.GMAT else 1
                    question_data = result[4]

                # Initialize section if not exists
                if section not in paper:
                    paper[section] = {}

                section_key = f"section{section_id}"
                if section_key not in paper[section]:
                    paper[section][section_key] = []

                # Add question if generation was successful
                if isinstance(question_data, dict) and "error" not in question_data:
                    # Process the question to convert options format and shuffle
                    processed_question = self._process_question_format(
                        question_data)
                    paper[section][section_key].append(processed_question)

        return paper

    def _process_question_format(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process question data to convert key-value options to shuffled array format.

        Args:
            question_data: Raw question data from AI with key-value options

        Returns:
            Processed question data with shuffled options array and converted answer
        """
        import random
        import copy

        # Create a deep copy to avoid modifying the original
        processed = copy.deepcopy(question_data)

        # Process main question options if they exist
        if "options" in processed and isinstance(processed["options"], dict):
            processed = self._convert_options_format(processed)

        # Process child questions for RC types
        if "childQuestions" in processed and isinstance(processed["childQuestions"], list):
            for i, child_q in enumerate(processed["childQuestions"]):
                if "options" in child_q and isinstance(child_q["options"], dict):
                    processed["childQuestions"][i] = self._convert_options_format(
                        child_q)

        return processed

    def _convert_options_format(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert key-value options format to shuffled array format.

        Input format:
        {
            "options": {"A": "text1", "B": "text2", "C": "text3", "D": "text4"},
            "answer": "C"
        }

        Output format:
        {
            "options": ["text2", "text1", "text4", "text3"],  # shuffled
            "answer": "text3"  # converted to actual text
        }
        """
        import random

        if "options" not in question or not isinstance(question["options"], dict):
            return question

        options_dict = question["options"]
        answer_key = question.get("answer", "")

        # Get the correct answer text before shuffling
        correct_answer_text = options_dict.get(answer_key, answer_key)

        # Create list of option texts
        option_texts = list(options_dict.values())

        # Shuffle the options
        random.shuffle(option_texts)

        # Update the question with new format
        question["options"] = option_texts
        question["answer"] = correct_answer_text

        return question

    def _extract_question_type(self, prompt: str) -> str:
        """Extract question type from prompt string."""
        if prompt.startswith("DS"):
            return "DS"
        elif prompt.startswith("S"):
            return "S"
        elif prompt.startswith("RC"):
            return "RC"
        elif prompt.startswith("CR"):
            return "CR"
        elif prompt.startswith("GI"):
            return "GI"
        elif prompt.startswith("TPA"):
            return "TPA"
        elif prompt.startswith("TA"):
            return "TA"
        elif prompt.startswith("MSR"):
            return "MSR"
        elif prompt.startswith("NE"):
            return "NE"
        elif prompt.startswith("PC"):
            return "PC"
        elif prompt.startswith("TC"):
            return "TC"
        elif prompt.startswith("SE"):
            return "SE"
        else:
            return "S"  # Default to simple

    def _count_total_questions(self, paper: Dict[str, Any]) -> int:
        """Count total questions in paper."""
        total = 0
        for section_name, sections in paper.items():
            if isinstance(sections, dict):
                for section_num, questions in sections.items():
                    if isinstance(questions, list):
                        total += len(questions)
        return total

    def _get_generator_class_for_prompt(self, prompt: str, section_type: SectionType) -> GeneratorClass:
        """Get generator class enum from prompt string."""
        question_type = self._extract_question_type(prompt)

        # Map question types to generator classes
        type_mapping = {
            "DS": GeneratorClass.Q_DS_gen,
            "S": GeneratorClass.Q_S_gen,
            "RC": GeneratorClass.V_PC_gen if section_type == SectionType.VERBAL else GeneratorClass.Q_PC_gen,
            "CR": GeneratorClass.V_S_gen,
            "GI": GeneratorClass.GI_gen,
            "TPA": GeneratorClass.TPA_gen,
            "TA": GeneratorClass.TA_gen,
            "MSR": GeneratorClass.MSR_gen,
            "NE": GeneratorClass.Q_NE_gen,
            "PC": GeneratorClass.Q_PC_gen,
            "TC": GeneratorClass.V_S_gen,
            "SE": GeneratorClass.V_S_gen
        }

        return type_mapping.get(question_type, GeneratorClass.Q_S_gen)

    def _get_simplified_json_template(self, generator_class: GeneratorClass) -> str:
        """Get simplified JSON template for specific question types."""
        question_type = self._extract_question_type_from_generator(
            generator_class)

        templates = {
            "DS": """{
  "type": "DS",
  "prompt": "simplified prompt",
  "content": {
    "passages": "simple text passage",
    "statements": ["statement 1", "statement 2"]
  },
  "question": "simple question text",
  "title": "question title",
  "options": {
    "A": "Statement 1 ALONE is sufficient, but statement 2 alone is not sufficient",
    "B": "Statement 2 ALONE is sufficient, but statement 1 alone is not sufficient", 
    "C": "BOTH statements TOGETHER are sufficient, but NEITHER statement ALONE is sufficient",
    "D": "EACH statement ALONE is sufficient",
    "E": "Statements 1 and 2 TOGETHER are NOT sufficient"
  },
  "answer": "C",
  "solution": "simple solution",
  "tag": ["Data Sufficiency"],
  "difficulty": 2
}""",
            "RC": """{
  "type": "RC",
  "prompt": "simplified prompt",
  "content": {
    "passage": "simple readable passage"
  },
  "childQuestions": [
    {
      "question": "simple question 1",
      "options": {
        "A": "option A text",
        "B": "option B text", 
        "C": "option C text",
        "D": "option D text"
      },
      "answer": "A"
    }
  ],
  "title": "reading passage",
  "tag": ["Reading Comprehension"],
  "difficulty": 2
}""",
            "NE": """{
  "type": "NE",
  "prompt": "simplified prompt",
  "question": "simple numeric question",
  "title": "numeric entry question",
  "answer": 42.00,
  "solution": "simple calculation",
  "tag": ["Numeric Entry"],
  "difficulty": 2
}""",
            "GI": """{
  "type": "GI",
  "prompt": "simplified prompt",
  "content": {
    "chart_type": "Bar Chart",
    "description": "simple chart description"
  },
  "question": "simple chart question",
  "title": "graphic interpretation",
  "answer": "simple answer",
  "solution": "simple explanation",
  "tag": ["Graphic Interpretation"],
  "difficulty": 2
}""",
            "TPA": """{
  "type": "TPA",
  "prompt": "simplified prompt",
  "question": "simple two part question",
  "title": "two part analysis",
  "parts": [
    {"question": "part 1", "answer": "Yes"},
    {"question": "part 2", "answer": "No"}
  ],
  "tag": ["Two Part Analysis"],
  "difficulty": 2
}"""
        }

        return templates.get(question_type, templates.get("S", """{
  "type": "S",
  "prompt": "simplified prompt",
  "question": "simple question text",
  "title": "simple question",
  "options": {
    "A": "option A text",
    "B": "option B text", 
    "C": "option C text",
    "D": "option D text"
  },
  "answer": "A",
  "solution": "simple solution",
  "tag": ["Problem Solving"],
  "difficulty": 2
}"""))

    def _get_ultra_simple_json_template(self, generator_class: GeneratorClass) -> str:
        """Get ultra-simple JSON template with minimal content."""
        question_type = self._extract_question_type_from_generator(
            generator_class)

        templates = {
            "DS": """{
  "type": "DS",
  "content": {
    "passages": "A store sells items",
    "statements": ["Statement 1 text", "Statement 2 text"]
  },
  "question": "What can we find?",
  "options": {
    "A": "Statement 1 ALONE is sufficient, but statement 2 alone is not sufficient",
    "B": "Statement 2 ALONE is sufficient, but statement 1 alone is not sufficient",
    "C": "BOTH statements TOGETHER are sufficient, but NEITHER statement ALONE is sufficient",
    "D": "EACH statement ALONE is sufficient",
    "E": "Statements 1 and 2 TOGETHER are NOT sufficient"
  },
  "answer": "C",
  "solution": "We need both statements",
  "difficulty": 2
}""",
            "RC": """{
  "type": "RC",
  "content": {
    "passage": "Simple text about a topic"
  },
  "childQuestions": [
    {
      "question": "What is the main idea?",
      "options": {
        "A": "First idea",
        "B": "Second idea",
        "C": "Third idea",
        "D": "Fourth idea"
      },
      "answer": "A"
    }
  ],
  "difficulty": 2
}""",
            "NE": """{
  "type": "NE",
  "question": "What is 2 plus 2?",
  "answer": 4.00,
  "solution": "Add 2 and 2",
  "difficulty": 2
}""",
            "GI": """{
  "type": "GI",
  "content": {
    "chart_type": "Bar Chart",
    "description": "Chart shows data"
  },
  "question": "Which bar is highest?",
  "answer": "Bar A",
  "solution": "Bar A is tallest",
  "difficulty": 2
}""",
            "TPA": """{
  "type": "TPA",
  "question": "Choose the best options",
  "parts": [
    {"question": "Is this true?", "answer": "Yes"},
    {"question": "Is that false?", "answer": "No"}
  ],
  "difficulty": 2
}"""
        }

        return templates.get(question_type, """{
  "type": "S",
  "question": "What is the answer?",
  "options": {
    "A": "First choice",
    "B": "Second choice",
    "C": "Third choice",
    "D": "Fourth choice"
  },
  "answer": "A",
  "solution": "First choice is correct",
  "difficulty": 2
}""")

    def _extract_question_type_from_generator(self, generator_class: GeneratorClass) -> str:
        """Extract question type from generator class enum."""
        class_name = generator_class.value

        if "DS" in class_name:
            return "DS"
        elif "PC" in class_name:
            return "RC"
        elif "NE" in class_name:
            return "NE"
        elif "GI" in class_name:
            return "GI"
        elif "TPA" in class_name:
            return "TPA"
        elif "TA" in class_name:
            return "TA"
        elif "MSR" in class_name:
            return "MSR"
        else:
            return "S"


# Factory function for creating unified mock generators
def create_mock_generator(exam_type: ExamType, difficulty: int) -> UnifiedMockGenerator:
    """
    Factory function for creating unified mock generators.

    Args:
        exam_type: The exam type (GMAT or GRE)
        difficulty: Mock exam difficulty level (1-5)

    Returns:
        Configured UnifiedMockGenerator instance
    """
    return UnifiedMockGenerator(exam_type, difficulty)
