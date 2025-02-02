import json, time, dotenv
from Mock.Verbal import Verbal
from Mock.Quants import Quants

from enum import Enum
import time
# region Quants generators:
from Quants.files.dataSufficiencyQuestionGeneration import DataSufficiencyQuestionGeneration as Q_DS_gen
from Quants.files.numericEntryQuestionGeneration import NumericEntryQuestionGeneration as Q_NE_gen
from Quants.files.parentChildQuestionGeneration import ParentChildQuestionGeneration as Q_PC_gen
from Quants.files.simpleQuestionGeneration import SimpleQuestionGeneration as Q_S_gen
# endregion

# region Verbal generators:
from Verbal.files.parentChildQuestionGeneration import ParentChildQuestionGeneration as V_PC_gen
from Verbal.files.simpleQuestionGeneration import SimpleQuestionGeneration as V_S_gen
# endregion 

from concurrent.futures import ThreadPoolExecutor, as_completed

class GeneratorClass(Enum):
    Q_PC_gen = "Q_PC_gen"
    Q_DS_gen = "Q_DS_gen"
    Q_NE_gen = "Q_NE_gen"
    Q_S_gen = "Q_S_gen"
    V_PC_gen = "V_PC_gen"
    V_S_gen = "V_S_gen"

GENERATOR_MAP = {
    GeneratorClass.Q_PC_gen: Q_PC_gen,
    GeneratorClass.Q_DS_gen: Q_DS_gen,
    GeneratorClass.Q_NE_gen: Q_NE_gen,
    GeneratorClass.Q_S_gen: Q_S_gen,
    GeneratorClass.V_PC_gen: V_PC_gen,
    GeneratorClass.V_S_gen: V_S_gen,
}
class GRE_Mock:
    def __init__(self, mock_difficulty) -> None:
        self.max_retries = 3
        self.mock_difficulty = mock_difficulty
        verbal = Verbal(mock_difficulty)
        self.verbal_prompts = verbal.generate_question_prompts()
        quants = Quants(mock_difficulty)
        self.quants_prompts = quants.generate_question_prompts()

    def generate_question_with_retry(self, exam_section: str, section_id: int, prompt: str, generator_class):
        retries = 0
        if not isinstance(generator_class, GeneratorClass):
            raise ValueError(f"Invalid generator_class: {generator_class}")
        while retries < self.max_retries:
            try:
                print(f"\nAttempting to generate {exam_section} question for section {section_id}")
                print(f"Using generator: {generator_class.name}")
                print(f"Prompt: {prompt}")
                
                question_generator_class = GENERATOR_MAP[generator_class]
                question_generator = question_generator_class(llm=None, prompt=prompt)
                question_data = question_generator.generate_question()
                
                if not question_data:
                    raise ValueError("Question generator returned None")
                    
                return [exam_section, f"section{section_id}", question_data]
            except Exception as e:
                retries += 1
                print(f"\nAttempt {retries} failed:")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print(f"Generator class: {question_generator_class.__name__}")
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

    def generate(self):
        # we need to prepare questions
        paper = {"GRE_Q": {"section1": [], "section2": []}, "GRE_V": {"section1": [], "section2": []}}
        
        # Generate Quants questions

        with ThreadPoolExecutor() as executor:
            futures = []
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
                            futures.append(executor.submit(self.generate_question_with_retry, "GRE_Q", section_id, prompt, generator_class))
                        else:
                            print(f"model: {model} and type: {type} not found\n\n")
                            pass
                section_id += 1
            # # Generate Verbal questions
            section_id = 1
            for section in self.verbal_prompts:
                for prompt in section:
                    if "rc" in prompt.lower():
                        futures.append(executor.submit(self.generate_question_with_retry, "GRE_V", section_id, prompt, GeneratorClass.V_PC_gen))
                    else:
                        futures.append(executor.submit(self.generate_question_with_retry, "GRE_V", section_id, prompt, GeneratorClass.V_S_gen))
                section_id += 1

            for future in as_completed(futures):
                question_data = future.result()
                if question_data:
                    exam_section, section_id, data = question_data
                    paper[exam_section][section_id].append(data)

        with open(f"GRE_paper-{time.strftime('%d-%m-%Y-%H-%M')}.json", "w") as f:
            json.dump(paper, f, indent=2)
        return paper

gre_mock = GRE_Mock(mock_difficulty=3)

paper = gre_mock.generate()

# json.dump(paper, open(f"paper-{time.strftime('%d-%m-%Y-%H-%M-%S')}.json", "w"), indent=2)
