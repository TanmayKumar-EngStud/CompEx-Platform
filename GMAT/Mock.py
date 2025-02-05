import json, time, dotenv
from Mock.Verbal import Verbal
from Mock.Quants import Quants
from Mock.Integrated_Reasoning import Integrated_Reasoning

import traceback
from enum import Enum
import time,os

from Integrated_Reasoning.files.GI import Generate_GI as GI_gen
from Integrated_Reasoning.files.TPA import Generate_TPA as TPA_gen
from Integrated_Reasoning.files.TA import Generate_TA as TA_gen
from Integrated_Reasoning.files.MSR import Generate_MSR as MSR_gen
from Quants.files.dataSufficiencyQuestionGeneration import DataSufficiencyQuestionGeneration as Q_DS_gen

# region Quants generators:
from Quants.files.simpleQuestionGeneration import SimpleQuestionGeneration as Q_S_gen

# endregion

# region Verbal generators:
from Verbal.files.parentChildQuestionGeneration import ParentChildQuestionGeneration as V_PC_gen
from Verbal.files.simpleQuestionGeneration import SimpleQuestionGeneration as V_S_gen
# endregion 

from concurrent.futures import ThreadPoolExecutor, as_completed
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

class GMAT_Mock:
    def __init__(self, mock_difficulty) -> None:
        self.max_retries = 3
        self.mock_difficulty = mock_difficulty
        verbal = Verbal(mock_difficulty)
        self.verbal_prompts = verbal.generate_question_prompts()
        quants = Quants(mock_difficulty)
        self.quants_prompts = quants.generate_question_prompts()
        ir = Integrated_Reasoning(mock_difficulty)
        self.ir_prompts = ir.generate_question_prompts()

    def generate_question_with_retry(self, exam_section: str, prompt: str, generator_class):
        retries = 0
        if not isinstance(generator_class, GeneratorClass):
            raise ValueError(f"Invalid generator class: {generator_class}")
        question_generator_class = GENERATOR_MAP[generator_class]
        while retries < self.max_retries:
            try:
                question_generator = question_generator_class(prompt=prompt)
                question_data = question_generator.generate_question()
                if not question_data:
                    raise ValueError("Question generator returned None")
                return [exam_section, question_data]
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
               
    def generate(self):
        # we need to prepare questions
        paper = {"GMAT_Q": {"section0":[]}, "GMAT_V": {"section0": []}, "GMAT_IR": {"section0": []}}
        with ThreadPoolExecutor() as executor:
            futures = []
            gi = 0
            tpa = 0
            ta = 0
            msr = 0
            q_ds = 0
            for prompt in self.ir_prompts:
                if "GI" in prompt and gi == 0:
                    futures.append(executor.submit(self.generate_question_with_retry, "GMAT_IR", prompt, GeneratorClass.GI_gen))
                    gi += 1
                elif "TA" in prompt and ta == 0:
                    futures.append(executor.submit(self.generate_question_with_retry, "GMAT_IR", prompt, GeneratorClass.TA_gen))
                    ta += 1
                elif "TPA" in prompt and tpa == 0:
                    futures.append(executor.submit(self.generate_question_with_retry, "GMAT_IR", prompt, GeneratorClass.TPA_gen))
                    tpa += 1
                elif "MSR" in prompt and msr == 0:
                    futures.append(executor.submit(self.generate_question_with_retry, "GMAT_IR", prompt, GeneratorClass.MSR_gen))
                    msr += 1
                elif "DS" in prompt and q_ds == 0:
                    futures.append(executor.submit(self.generate_question_with_retry, "GMAT_IR", prompt, GeneratorClass.Q_DS_gen))
                    q_ds += 1

            # for prompt in self.quants_prompts:
            #     futures.append(executor.submit(self.generate_question_with_retry, "GMAT_Q", prompt, GeneratorClass.Q_S_gen)) 
            # for prompt in self.verbal_prompts:
            #     if "rc" in prompt.lower():
            #         futures.append(executor.submit(self.generate_question_with_retry, "GMAT_V", prompt, GeneratorClass.V_PC_gen))
            #     else:
            #         futures.append(executor.submit(self.generate_question_with_retry, "GMAT_V", prompt, GeneratorClass.V_S_gen))

            for future in as_completed(futures):
                question_data = future.result()
                if question_data:
                    exam_section, data = question_data
                    paper[exam_section]["section0"].append(data)

        with open(f"GMAT_paper-{time.strftime('%d-%m-%Y-%H-%M')}.json", "w") as f:
            json.dump(paper, f, indent=2)

        return paper

gmat_mock = GMAT_Mock(mock_difficulty=3)

paper = gmat_mock.generate()

# json.dump(paper, open(f"paper-{time.strftime('%d-%m-%Y-%H-%M-%S')}.json", "w"), indent=2)
