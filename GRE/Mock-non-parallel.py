import json, time, dotenv
from Mock.Verbal import Verbal
from Mock.Quants import Quants

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

class GRE_Mock:
    def __init__(self, mock_difficulty) -> None:
        self.max_retries = 3
        self.mock_difficulty = mock_difficulty
        verbal = Verbal(mock_difficulty)
        self.verbal_prompts = verbal.generate_question_prompts()
        quants = Quants(mock_difficulty)
        self.quants_prompts = quants.generate_question_prompts()

    def generate_question_with_retry(self, exam_section, section_id, prompt, generator_class):
        retries = 0
        while retries < self.max_retries:
            try:
                question_generator = generator_class(llm=None, prompt=prompt)
                question_data = question_generator.generate_question()
                return [exam_section, f"section{section_id}", question_data]
            except Exception as e:
                retries += 1
                if retries == self.max_retries:
                    print(f"Failed after {self.max_retries} attempts due to: {str(e)}")
                    return None
                print(f"Attempt {retries} failed, retrying: {str(e)}")

    def generate(self):
        # we need to prepare questions
        paper = {"GRE_Q": {"section1": [], "section2": []}, "GRE_V": {"section1": [], "section2": []}}
        
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
                        "parent_child": Q_PC_gen,
                        "ds": Q_DS_gen,
                        "ne": Q_NE_gen,
                        "mcq_single": Q_S_gen,
                        "mcq_multiple": Q_S_gen
                    }
                    
                    generator_class = generator_map.get(type, None)  # parent_child
                    if not generator_class:
                        generator_class = generator_map.get(model, None)  # ds, ne, mcq_single, mcq_multiple
                    if generator_class:
                        question_data = self.generate_question_with_retry(
                            "GRE_Q",
                            section_id,
                            prompt,
                            generator_class
                        )
                        if question_data:
                            exam_section, section_key, data = question_data
                            paper[exam_section][section_key].append(data)
                    else:
                        print(f"No generator found for model: {model} and type: {type}")
            section_id += 1

        # Generate Verbal questions
        section_id = 1
        for prompt in self.verbal_prompts:
            if isinstance(prompt, dict) and "rc" in prompt:
                question_data = self.generate_question_with_retry(
                    "GRE_V",
                    section_id,
                    prompt["rc"],
                    V_PC_gen
                )
            else:
                question_data = self.generate_question_with_retry(
                    "GRE_V",
                    section_id,
                    prompt,
                    V_S_gen
                )
            if question_data:
                exam_section, section_key, data = question_data
                paper[exam_section][section_key].append(data)
            section_id += 1

        return paper

gre_mock = GRE_Mock(mock_difficulty=3)
paper = gre_mock.generate()

json.dump(paper, open(f"paper-{time.strftime('%d-%m-%Y-%H-%M-%S')}.json", "w"), indent=2)