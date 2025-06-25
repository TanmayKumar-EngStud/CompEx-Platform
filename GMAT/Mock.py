import json, time, dotenv
# GMAT.
from GMAT.Mock_prompts.Verbal import Verbal_prompts
from GMAT.Mock_prompts.Quants import Quants_prompts
from GMAT.Mock_prompts.Integrated_Reasoning import Integrated_Reasoning_prompts

import traceback
from enum import Enum
import time, os, threading
from GMAT.Integrated_Reasoning.files.GI import Generate_GI as GI_gen
from GMAT.Integrated_Reasoning.files.TPA import Generate_TPA as TPA_gen
from GMAT.Integrated_Reasoning.files.TA import Generate_TA as TA_gen
from GMAT.Integrated_Reasoning.files.MSR import Generate_MSR as MSR_gen
from GMAT.Quants.files.dataSufficiencyQuestionGeneration import DataSufficiencyQuestionGeneration as Q_DS_gen

# region Quants generators:
from GMAT.Quants.files.simpleQuestionGeneration import SimpleQuestionGeneration as Q_S_gen
# endregion

# region Verbal generators:
from GMAT.Verbal.files.parentChildQuestionGeneration import ParentChildQuestionGeneration as V_PC_gen
from GMAT.Verbal.files.simpleQuestionGeneration import SimpleQuestionGeneration as V_S_gen
# endregion 

from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

# Import unified threading components
from core.threading import APIThreadPoolManager, ThreadConfig
from core.enums.exam_types import ExamType

def clear_terminal():
    os.system('clear')
clear_terminal()
class GeneratorClass(Enum):
    Q_DS_gen = "Q_DS_gen"
    Q_S_gen = "Q_S_gen"
    V_PC_gen = "V_PC_gen"
    V_S_gen = "V_S_gen"
    GI_gen = "GI_gen"
    TPA_gen = "TPA_gen"
    TA_gen = "TA_gen"
    MSR_gen = "MSR_gen"

GENERATOR_MAP = {
    GeneratorClass.Q_DS_gen: Q_DS_gen,
    GeneratorClass.Q_S_gen: Q_S_gen,
    GeneratorClass.V_PC_gen: V_PC_gen,
    GeneratorClass.V_S_gen: V_S_gen,
    GeneratorClass.GI_gen: GI_gen,
    GeneratorClass.TPA_gen: TPA_gen,
    GeneratorClass.TA_gen: TA_gen,
    GeneratorClass.MSR_gen: MSR_gen,
}

# Legacy APIThreadPoolManager removed - now using unified core.threading.APIThreadPoolManager

class GMAT_Mock:

    def __init__(self, mock_difficulty) -> None:
        self.max_retries = 3
        self.mock_difficulty = mock_difficulty
        verbal = Verbal_prompts(mock_difficulty)
        self.verbal_prompts = verbal.generate_question_prompts()
        quants = Quants_prompts(mock_difficulty)
        self.quants_prompts = quants.generate_question_prompts()
        ir = Integrated_Reasoning_prompts(mock_difficulty)
        self.ir_prompts = ir.generate_question_prompts()

    def generate_question_with_retry(self, api_state, lock, exam_section: str, prompt: str, generator_class, api_itr):
        """
        Generate question with retry logic using the unified API state format.
        
        Args:
            api_state: APIState object or dict containing API state information
            lock: Threading lock for this API instance
            exam_section: Section name for the question
            prompt: Generation prompt
            generator_class: Generator class enum
            api_itr: API iterator/index
            
        Returns:
            List in format: [api_itr, start_time, request_count, exam_section, question_data]
        """
        retries = 0
        if not isinstance(generator_class, GeneratorClass):
            raise ValueError(f"Invalid generator class: {generator_class}")
        question_generator_class = GENERATOR_MAP[generator_class]
        
        # Handle both APIState objects and legacy dict format
        if hasattr(api_state, 'to_dict'):
            global_state = api_state.to_dict()
        else:
            global_state = api_state
            
        while retries < self.max_retries:
            try:
                question_generator = question_generator_class(global_state, lock, api_itr, prompt=prompt)
                question_data = question_generator.generate_question()
                if not question_data:
                    raise ValueError("Question generator returned None")
                return [api_itr, global_state["start_time"], global_state["request_count"], exam_section, question_data]
            except Exception as e:
                retries += 1
                print(f"\nAttempt {retries} failed:")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print(f"Generator class: {question_generator_class.__name__}")
                if hasattr(e, '__traceback__'):
                    print("Traceback:")
                    traceback.print_tb(e.__traceback__)
                    print(f"Error: {str(e)}")
                
                if retries == self.max_retries:
                    print(f"\nFailed after {self.max_retries} attempts for:")
                    print(f"Section: {exam_section}")
                    print(f"Generator: {generator_class.name}")
                    print(f"Prompt: {prompt}")
                    return None
                print(f"\nAttempt {retries} failed, retrying: {str(e)}\nPrompt: {prompt}\n\n")

    def generate(self, num_APIs):
        """
        Generate GMAT paper using unified thread pool manager.
        
        Args:
            num_APIs: Number of API instances to use for concurrent generation
            
        Returns:
            Complete GMAT paper with all sections
        """
        # Create GMAT-specific configuration
        config = ThreadConfig.create_gmat_config(max_workers=num_APIs)
        
        # Paper structure is handled by the unified manager
        paper = {"GMAT_Q": {"section0":[]}, "GMAT_V": {"section0": []}, "GMAT_IR": {"section0": []}}
        
        # Initialize unified thread pool manager
        with APIThreadPoolManager(config, paper) as manager:
            task_prompts = []
            
            # region adding all the tasks inside the task_prompts
            for prompt in self.ir_prompts:
                if "GI" in prompt: 
                    task_prompts.append((self.generate_question_with_retry, "GMAT_IR", prompt, GeneratorClass.GI_gen))
                elif "TA" in prompt:
                    task_prompts.append((self.generate_question_with_retry, "GMAT_IR", prompt, GeneratorClass.TA_gen))
                elif "TPA" in prompt:
                    task_prompts.append((self.generate_question_with_retry, "GMAT_IR", prompt, GeneratorClass.TPA_gen))
                elif "MSR" in prompt:
                    task_prompts.append((self.generate_question_with_retry, "GMAT_IR", prompt, GeneratorClass.MSR_gen))
                elif "DS" in prompt:
                    task_prompts.append((self.generate_question_with_retry, "GMAT_IR", prompt, GeneratorClass.Q_DS_gen))
                    
            for prompt in self.quants_prompts:
                task_prompts.append((self.generate_question_with_retry, "GMAT_Q", prompt, GeneratorClass.Q_S_gen))
                
            for prompt in self.verbal_prompts:
                if "rc" in prompt.lower():
                    task_prompts.append((self.generate_question_with_retry, "GMAT_V", prompt, GeneratorClass.V_PC_gen))
                else:
                    task_prompts.append((self.generate_question_with_retry, "GMAT_V", prompt, GeneratorClass.V_S_gen))
            # endregion

            def create_task(method, section, prompt, gen_class):
                def task(api_state, lock, api_idx):
                    return method(api_state, lock, section, prompt, gen_class, api_idx)
                return task
            
            # Submit all tasks to the unified manager
            for method, section, prompt, gen_class in task_prompts:
                manager.add_task(create_task, method, section, prompt, gen_class)
                
            # Execute all tasks and get the complete paper
            paper = manager.execute_all()
            
        return paper

# start_time = time.time()
# gmat_mock = GMAT_Mock(mock_difficulty=1)

# paper = gmat_mock.generate(8)

# json.dump(paper, open(f"paper-NIGGA.json", "w"), indent=2)
# print("paper generated")
# end_time = time.time()
# print(f"Time taken: {end_time - start_time} seconds")