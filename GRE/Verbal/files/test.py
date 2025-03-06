import json
import os

from parentChildQuestionGeneration import ParentChildQuestionGeneration
from simpleQuestionGeneration import SimpleQuestionGeneration

from enum import Enum

class GeneratorClass(Enum):
    PCQ = "PCQ"
    SQ = "SQ"
    SE = "SE"
GENERATOR_MAP = {
    GeneratorClass.PCQ: ParentChildQuestionGeneration,
    GeneratorClass.SQ: SimpleQuestionGeneration,
    GeneratorClass.SE: SimpleQuestionGeneration,
}

PREDEFINED_PROMPTS = {
    GeneratorClass.PCQ: "<science> - <rc-l> - <difficulty-level: 5> - <vocabulary-level:3>",
    GeneratorClass.SQ: "<Philosophy> - <TC-3> - <difficulty-level: 1> - <vocabulary-level:2>",
    GeneratorClass.SE: "<History> - <SE> - <difficulty-level: 3> - <vocabulary-level:3>",
}

os.system('clear')

def test(generator_class: GeneratorClass, idx=1):
    question_generator_class = GENERATOR_MAP[generator_class]
    test_prompt2 = PREDEFINED_PROMPTS[generator_class]
    msr_generator2 = question_generator_class(test_prompt2, idx)
    question_data2 = msr_generator2.generate_question()
    
    # Save the response to a JSON file in the same directory
    output_path = os.path.join(os.path.dirname(__file__), f"./tests/test_{generator_class.value}.json")
    with open(output_path, "w") as f:

        json.dump(question_data2, fp=f, indent=2)
    
    print(f"Test output saved to: {output_path}")
    return question_data2

if __name__ == "__main__":
    test(GeneratorClass.SE, 2)