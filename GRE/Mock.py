import json, time, dotenv
# GRE.
from GRE.Mock_prompts.Verbal import Verbal_prompts
from GRE.Mock_prompts.Quants import Quants_prompts

from enum import Enum
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import asyncio

# Import unified threading components
from core.threading import APIThreadPoolManager, ThreadConfig
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType

# Import factory pattern
from core.factories.question_generator_factory import get_question_generator_factory

# Legacy generator enum for backward compatibility
class GeneratorClass(Enum):
    Q_PC_gen = "Q_PC_gen"
    Q_DS_gen = "Q_DS_gen"
    Q_NE_gen = "Q_NE_gen"
    Q_S_gen = "Q_S_gen"
    V_PC_gen = "V_PC_gen"
    V_S_gen = "V_S_gen"

# Legacy mapping for backward compatibility
LEGACY_GENERATOR_MAPPING = {
    GeneratorClass.Q_PC_gen: (QuestionType.READING_COMPREHENSION, SectionType.QUANTITATIVE),
    GeneratorClass.Q_DS_gen: (QuestionType.DATA_SUFFICIENCY, SectionType.QUANTITATIVE),
    GeneratorClass.Q_NE_gen: (QuestionType.NUMERIC_ENTRY, SectionType.QUANTITATIVE),
    GeneratorClass.Q_S_gen: (QuestionType.PROBLEM_SOLVING, SectionType.QUANTITATIVE),
    GeneratorClass.V_PC_gen: (QuestionType.READING_COMPREHENSION, SectionType.VERBAL),
    GeneratorClass.V_S_gen: (QuestionType.TEXT_COMPLETION, SectionType.VERBAL),
}
# Legacy APIThreadPoolManager removed - now using unified core.threading.APIThreadPoolManager

class GRE_Mock:
    def __init__(self, mock_difficulty) -> None:
        self.max_retries = 3
        self.mock_difficulty = mock_difficulty
        verbal = Verbal_prompts(mock_difficulty)
        self.verbal_prompts = verbal.generate_question_prompts()
        quants = Quants_prompts(mock_difficulty)
        self.quants_prompts = quants.generate_question_prompts()

    def generate_question_with_retry(self, api_state, lock, exam_section: str, section_id: int, prompt: str, generator_class, api_itr):
        """
        Generate question with retry logic using the unified factory pattern.
        
        Args:
            api_state: APIState object or dict containing API state information
            lock: Threading lock for this API instance
            exam_section: Section name for the question
            section_id: Section ID number
            prompt: Generation prompt
            generator_class: Generator class enum
            api_itr: API iterator/index
            
        Returns:
            List in format: [api_itr, start_time, request_count, exam_section, section_id, question_data]
        """
        retries = 0
        if not isinstance(generator_class, GeneratorClass):
            raise ValueError(f"Invalid generator_class: {generator_class}")
        
        # Get question and section types from legacy mapping
        if generator_class not in LEGACY_GENERATOR_MAPPING:
            raise ValueError(f"Unknown generator class: {generator_class}")
        
        question_type, section_type = LEGACY_GENERATOR_MAPPING[generator_class]
            
        # Handle both APIState objects and legacy dict format
        if hasattr(api_state, 'to_dict'):
            global_state = api_state.to_dict()
        else:
            global_state = api_state
            
        # Get factory instance
        factory = get_question_generator_factory()
            
        while retries < self.max_retries:
            try:
                # Create generator using factory
                question_generator = factory.create_generator(
                    exam_type=ExamType.GRE,
                    question_type=question_type,
                    section_type=section_type,
                    global_state=global_state,
                    lock=lock,
                    api_idx=api_itr,
                    prompt=prompt
                )
                
                if question_generator is None:
                    raise ValueError(f"Factory failed to create generator for {generator_class}")
                
                question_data = question_generator.generate_question(prompt)
                
                if not question_data:
                    raise ValueError("Question generator returned None")
                    
                return [api_itr, global_state["start_time"], global_state["request_count"], exam_section, f"section{section_id}", question_data]
            except Exception as e:
                retries += 1
                print(f"\nAttempt {retries} failed:")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print(f"Generator class: {generator_class}")
                if hasattr(e, '__traceback__'):
                    import traceback
                    print("Traceback:")
                    traceback.print_tb(e.__traceback__)
                
                if retries == self.max_retries:
                    print(f"\nFailed after {self.max_retries} attempts for:")
                    print(f"Section: {exam_section}")
                    print(f"Generator: {generator_class.name}")
                    print(f"Prompt: {prompt}")
                    return None
                print(f"\nAttempt {retries} failed, retrying: {str(e)}\nPrompt: {prompt}\n\n")

    def generate(self, num_APIs):
        """
        Generate GRE paper using unified thread pool manager.
        
        Args:
            num_APIs: Number of API instances to use for concurrent generation
            
        Returns:
            Complete GRE paper with all sections
        """
        # Create GRE-specific configuration
        config = ThreadConfig.create_gre_config(max_workers=num_APIs)
        
        # Paper structure is handled by the unified manager
        paper = {"GRE_Q": {"section1": [], "section2": []}, "GRE_V": {"section1": [], "section2": []}}
        
        # Initialize unified thread pool manager
        with APIThreadPoolManager(config, paper) as manager:
            task_prompts = []
            
            # Generate Quants questions
            section_id = 1
            for section in self.quants_prompts:
                for prompt_array in section:
                    for key, value in prompt_array.items():
                        model, type = key.split(" ")
                        prompt = value
                        if "mcq_multiple" in model:
                            prompt = value + " (multi-correct MCQ)"
                        
                        generator_map = {
                                "parent_child": GeneratorClass.Q_PC_gen,
                                "ds": GeneratorClass.Q_DS_gen,
                                "ne": GeneratorClass.Q_NE_gen,
                                "mcq_single": GeneratorClass.Q_S_gen,
                                "mcq_multiple": GeneratorClass.Q_S_gen
                        }
                        
                        generator_class =None
                            # parent_child
                        if "parent_child" in type:
                            prompt = f"{type}:- {prompt}"
                            generator_class = GeneratorClass.Q_PC_gen

                        if not generator_class:
                            generator_class = generator_map.get(model, None)  # ds, ne, mcq_single, mcq_multiple
                        
                        if generator_class:
                            task_prompts.append((self.generate_question_with_retry, "GRE_Q", section_id, prompt, generator_class))
                        else:
                            print(f"model: {model} and type: {type} not found\n\n")
                            pass
                section_id += 1
                
            # Generate Verbal questions
            section_id = 1
            for section in self.verbal_prompts:
                for prompt in section:
                    if "rc" in prompt.lower():
                        task_prompts.append((self.generate_question_with_retry, "GRE_V", section_id, prompt, GeneratorClass.V_PC_gen))
                    else:
                        task_prompts.append((self.generate_question_with_retry, "GRE_V", section_id, prompt, GeneratorClass.V_S_gen))
                section_id += 1

            def create_task(method, exam_section, section_id, prompt, gen_class):
                def task(api_state, lock, api_idx):
                    return method(api_state, lock, exam_section, section_id, prompt, gen_class, api_idx)
                return task
                
            # Submit all tasks to the unified manager
            for method, exam_section, section_id, prompt, gen_class in task_prompts:
                manager.add_task(create_task, method, exam_section, section_id, prompt, gen_class)
            
            # Execute all tasks and get the complete paper
            paper = manager.execute_all()
            
        return paper
# start_time = time.time()
# gre_mock = GRE_Mock(mock_difficulty=3)

# paper = gre_mock.generate(8)
# print("Paper generated")
# end_time = time.time()
# print(f"Time taken: {end_time - start_time:.2f} seconds")
# json.dump(paper, open(f"GRE-paper.json", "w"), indent=2)
