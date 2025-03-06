import random, os, sys, json
from dotenv import load_dotenv
# GMAT.Quants.files.
from google import genai
from questionComponents import DataSufficiencyQuestion
import re
class DataSufficiencyQuestionGeneration:
    def __init__(self, prompt, api_IDX=1):
        load_dotenv()
        api_key = os.getenv(f"API_{api_IDX}")
        self.llm = genai.Client(api_key=api_key)
        with open(os.path.join(os.path.dirname(__file__), "../System_instructions/GMAT-Quants-Data-Sufficiency-Questions.txt"), "r") as f:
            self.system_instructions = f.read()
        self.prompt = prompt
        self.questionData = {}
    def generate_question(self):
        questionContent = DataSufficiencyQuestion(self.llm, self.system_instructions, self.prompt)
        self.questionData["type"] = "Data Sufficiency"
        self.questionData["prompt"] = self.prompt
        passages, statements, question = questionContent.generate_questionText()
        self.questionData["content"] = {"passages": passages, "statements": statements}
        self.questionData["question"] = question
        self.questionData["title"] = questionContent.generate_questionTitle()
        self.questionData["solution"], self.questionData["answer"] = questionContent.generate_questionSolution()
        self.questionData["options"] = ["Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient", "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient", "BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient", "EITHER statement ALONE is sufficient", "Statements (1) and (2) TOGETHER are NOT sufficient"]
        self.questionData["answer"] = self.questionData["options"][ord(self.questionData["answer"]) - ord("A")]
        difficulty_search = re.search(r"difficulty_level: (\d+)", self.prompt)
        difficulty = 1
        if difficulty_search:
            difficulty = int(difficulty_search.group(1))
        self.questionData["difficulty"] = difficulty
        self.questionData["tag"] = self.prompt.split(" - ")[0].strip("<>").strip("[]").split(",")
        return self.questionData