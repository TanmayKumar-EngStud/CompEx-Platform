import json
import os
from MSR import Generate_MSR
from GI import Generate_GI
from TA import Generate_TA
from TPA import Generate_TPA
from enum import Enum

class GeneratorClass(Enum):
    Generate_MSR = "MSR"
    Generate_GI = "GI"
    Generate_TA = "TA"
    Generate_TPA = "TPA"

GENERATOR_MAP = {
    GeneratorClass.Generate_MSR: Generate_MSR,
    GeneratorClass.Generate_GI: Generate_GI,
    GeneratorClass.Generate_TA: Generate_TA,
    GeneratorClass.Generate_TPA: Generate_TPA
}

PREDEFINED_PROMPTS = {
    GeneratorClass.Generate_MSR: "MSR - <total_child_questions: 2> - <Finance> - <Logical Reasoning> - <MCQ (5 options MCQ)> - <difficulty_level: 5>",
    GeneratorClass.Generate_GI: "GI - <Economics> - <Data Interpretation> - <Pie Chart> - <difficulty_level: 2>",
    GeneratorClass.Generate_TA: "TA - <Taxation> - <Data Synthesis> - <Time_series Table> - <True/False type> - <difficulty_level: 1>",
    GeneratorClass.Generate_TPA: "TPA - <Analysis (over any Miscellaneous topic)> - <Data Interpretation> - <Passage> - <difficulty_level: 2>"
}

os.system('clear')

def test(generator_class: GeneratorClass, idx =1):
    question_generator_class = GENERATOR_MAP[generator_class]
    # Test prompt format: "TA - <theme> - <focused_skill> - <table_type> - <question_type> - <difficulty_level>"
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
    test(GeneratorClass.Generate_TPA, 1)