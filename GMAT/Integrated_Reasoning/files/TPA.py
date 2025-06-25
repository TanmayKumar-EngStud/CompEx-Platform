# GMAT.Integrated_Reasoning.files.
# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter
import random
import json
from google import genai
from dotenv import load_dotenv
import os
import re


class Generate_TPA:
    def __init__(self, global_state, lock, api_IDX, prompt):
        load_dotenv()
        self.global_state = global_state
        self.lock = lock
        api_key = os.getenv(f"API_{api_IDX}")
        self.llm = genai.Client(api_key=api_key)
        with open(os.path.join(os.path.dirname(__file__), "../System_instructions/Two-Part-Analysis.txt"), "r") as f:
            self.system_instructions = f.read()
        self.prompt = prompt
        self.questionData = {}

    def generate_question(self):
        difficulty_search = re.search(r"difficulty_level: (\d+)", self.prompt)
        difficulty = 1
        if difficulty_search:
            difficulty = int(difficulty_search.group(1))

        # Create unified component and wrap with GMAT adapter
        component = create_question_component(
            question_type=QuestionType.TWO_PART_ANALYSIS,
            llm=self.llm,
            system_instructions=self.system_instructions,
            global_state=self.global_state,
            lock=self.lock,
            prompt=self.prompt,
            exam_type=ExamType.GMAT
        )
        tpa = GMATAdapter.adapt_two_part_analysis(component)

        # Generate question text and components
        parentQuestionContent = tpa.generate_ParentQuestionContent()
        self.questionData["type"] = "TPA"
        self.questionData["prompt"] = self.prompt
        self.questionData["content"] = [parentQuestionContent]

        # region preparing difficulty for child Questions
        d1 = difficulty + random.randint(-1, 1)
        d2 = difficulty + random.randint(-1, 1)
        if d1 < 1:
            d1 = 1
        if d2 < 1:
            d2 = 1
        if d1 > 5:
            d1 = 5
        if d2 > 5:
            d2 = 5
        # endregion

        # region generating child questions
        questions = tpa.generate_QuestionText([d1, d2])
        if not questions or len(questions) < 2:
            print("Error: Failed to generate questions or insufficient questions returned")
            return None
        
        q1 = {}
        q2 = {}
        q1["question"] = questions[0]
        q2["question"] = questions[1]

        solutions = tpa.generate_QuestionSolution()
        if not solutions or len(solutions) < 2:
            print("Error: Failed to generate solutions or insufficient solutions returned")
            return None
        q1["solution"] = solutions[0]
        q2["solution"] = solutions[1]
        common_options, answers = tpa.generate_QuestionOptions()
        if not common_options or not answers:
            print("Error: Failed to generate options or answers")
            return None
        
        try:
            ans1 = common_options[answers["question1"]]
            ans2 = common_options[answers["question2"]]
            q1["answer"] = ans1
            q2["answer"] = ans2
        except (KeyError, TypeError) as e:
            print(f"Error: Invalid options or answers structure: {e}")
            return None

        title = tpa.generate_QuestionTitle()
        self.questionData["title"] = title or "Two Part Analysis Question"
        option_list = list(common_options.values())
        random.shuffle(option_list)
        q1["type"] = "TPA"
        q2["type"] = "TPA"
        q1["title"] = title
        q2["title"] = title
        q1["prompt"] = self.prompt
        q2["prompt"] = self.prompt
        q1["options"] = option_list
        q2["options"] = option_list
        q1["difficulty"] = d1
        q2["difficulty"] = d2
        q1["tags"] = [self.prompt.split(" - ")[1].strip().strip("<>").strip()]
        q2["tags"] = [self.prompt.split(" - ")[1].strip().strip("<>").strip()]
        # endregion
        self.questionData["questions"] = [q1, q2]

        # Set tags and difficulty
        self.questionData["tags"] = ["TPA", self.prompt.split(
            " - ")[1].strip().strip("<>").strip()]
        self.questionData["difficulty"] = difficulty

        return self.questionData

# g = Generate_TPA("<Business> - <Quantitative Skills> - <difficulty_level: 3> - <Bar Chart>")
# res = g.generate_TPA()
# json.dump(res, open("tpa-component.json", "w"))
