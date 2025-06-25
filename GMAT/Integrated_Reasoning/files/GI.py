import random
import json
import os
import re
from google import genai
from dotenv import load_dotenv

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter


class Generate_GI:
    def __init__(self, global_state, lock, api_IDX, prompt):
        load_dotenv()
        self.global_state = global_state
        self.lock = lock
        api_key = os.getenv(f"API_{api_IDX}")
        self.llm = genai.Client(api_key=api_key)
        with open(os.path.join(os.path.dirname(__file__), "../System_instructions/Graphic-Interpretation.txt"), "r") as f:
            self.system_instructions = f.read()
        self.prompt = prompt
        self.questionData = {}

    def generate_question(self):
        # Create unified component and wrap with GMAT adapter
        component = create_question_component(
            question_type=QuestionType.GRAPHIC_INTERPRETATION,
            llm=self.llm,
            system_instructions=self.system_instructions,
            global_state=self.global_state,
            lock=self.lock,
            prompt=self.prompt,
            exam_type=ExamType.GMAT
        )
        gi = GMATAdapter.adapt_graphic_interpretation(component)
        self.questionData["type"] = "GI"
        self.questionData["prompt"] = self.prompt
        self.questionData["content"] = gi.generate_questionGraph()
        self.questionData["question"] = gi.generate_questionText()
        self.questionData["title"] = gi.generate_questionTitle()
        self.questionData["solution"] = gi.generate_questionSolution()
        options_list, correct_option = gi.generate_questionOptions()
        idx = 0
        answer_list = []
        options = []
        while idx < len(options_list.values()):
            answer_list.append(
                options_list[f"blank_{idx+1}"][correct_option[f"blank_{idx+1}"]])
            opts = list(options_list[f"blank_{idx+1}"].values())
            random.shuffle(opts)
            options.append(opts)
            idx += 1
        self.questionData["options"] = options
        self.questionData["answer"] = answer_list
        self.questionData["tags"] = ["GI", self.prompt.split(
            "-")[2].strip().strip('<>').strip()]
        difficulty = re.search(r"<difficulty_level: (\d+)>", self.prompt)
        self.questionData["difficulty"] = int(difficulty.group(1))
        return self.questionData

# g = Generate_GI("<GI> - <Bar Chart> - <difficulty_level: 4>")
# content = g.generate_GI()
# json.dump(content, open(os.path.join(os.path.dirname(__file__), "GI-component.json"), "w"))
