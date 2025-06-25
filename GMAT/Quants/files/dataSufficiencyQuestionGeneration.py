import random, os, sys, json, re
from dotenv import load_dotenv
from google import genai

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter
class DataSufficiencyQuestionGeneration:
    def __init__(self, global_state, lock, api_IDX, prompt):
        load_dotenv()
        self.global_state = global_state
        self.lock = lock
        api_key = os.getenv(f"API_{api_IDX}")
        self.llm = genai.Client(api_key=api_key)
        with open(os.path.join(os.path.dirname(__file__), "../System_instructions/GMAT-Quants-Data-Sufficiency-Questions.txt"), "r") as f:
            self.system_instructions = f.read()
        self.prompt = prompt
        self.questionData = {}
    def generate_question(self):
        # Create unified component and wrap with GMAT adapter
        component = create_question_component(
            question_type=QuestionType.DATA_SUFFICIENCY,
            llm=self.llm,
            system_instructions=self.system_instructions,
            global_state=self.global_state,
            lock=self.lock,
            prompt=self.prompt,
            exam_type=ExamType.GMAT
        )
        questionContent = GMATAdapter.adapt_data_sufficiency_question(component)
        self.questionData["type"] = "Data Sufficiency"
        self.questionData["prompt"] = self.prompt
        passages, statements, question = questionContent.generate_questionText()
        self.questionData["content"] = {"passages": passages, "statements": statements}
        self.questionData["question"] = question
        self.questionData["title"] = questionContent.generate_questionTitle()
        self.questionData["solution"], self.questionData["answer"] = questionContent.generate_questionSolution()
        self.questionData["options"] = [
            "Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient", 
            "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient", 
            "BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient", 
            "EITHER statement ALONE is sufficient", 
            "Statements (1) and (2) TOGETHER are NOT sufficient"
        ]
        self.questionData["answer"] = self.questionData["options"][ord(self.questionData["answer"]) - ord("A")]
        difficulty_search = re.search(r"difficulty_level: (\d+)", self.prompt)
        difficulty = 1
        if difficulty_search:
            difficulty = int(difficulty_search.group(1))
        self.questionData["difficulty"] = difficulty
        self.questionData["tag"] = self.prompt.split(" - ")[0].strip("<>").strip("[]").split(",")
        return self.questionData