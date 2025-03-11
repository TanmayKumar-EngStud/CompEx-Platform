from dotenv import load_dotenv
from google import genai
import os, json
# GRE.Quants.files.
from Quants.files.questionComponents import DataSufficiencyQuestion
import re
class DataSufficiencyQuestionGeneration:
    def __init__(self, global_state, lock, api_IDX, prompt):
        load_dotenv()
        api_key = os.getenv(f"API_{api_IDX}")
        self.global_state = global_state
        self.lock = lock
        self.llm = genai.Client(api_key = api_key)
        with open(os.path.join(os.path.dirname(__file__), "../System_instructions/GRE-Quants-Data-Sufficiency-Questions.txt"), "r") as f:
            self.system_instructions = f.read()
        self.prompt = prompt
        self.questionData = {}
    def generate_question(self):
        self.questionData["prompt"] = self.prompt
        self.questionData["type"] = "DS"
        pattern = r'<difficulty-level: (\d+)>'
        match = re.search(pattern, self.prompt)
        self.questionData["difficulty"] = int(match.group(1))
        try:
            match = re.search(r"<(.*?)>", self.prompt)
            tag = ["DS"]
            if match:
                first_content = match.group(1)
                tag.append(first_content)
            self.questionData["tags"] = tag
        except Exception as e:
            raise Exception(f"Error: {self.prompt} the length of the prompt is {len(self.prompt.split('-'))}")
        dataSufficiencyQuestion = DataSufficiencyQuestion(self.llm, self.system_instructions, self.global_state, self.prompt, self.lock)
        content = {}

        passage, statements, question = dataSufficiencyQuestion.generate_questionText()
        content["passage"] = passage
        content["statements"] = statements
        if len(statements) == 1:
            value = statements[0]
            match = re.search(r'\bstatement\b[^0-9]*?\b2\b', value, re.IGNORECASE)
            if match:
                index = match.start()
                part1 = value[:index]
                part2 = value[index:]
                part = [part1, part2]
                statements = part
            else:
                raise Exception("Statement 2 not found")
        self.questionData["content"] = content
        self.questionData["question"] = question
        
        self.questionData["title"] = dataSufficiencyQuestion.generate_questionTitle()

        self.questionData["solution"], self.questionData["answer"] = dataSufficiencyQuestion.generate_questionSolution()
        self.questionData["options"] = ["Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient", "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient", "BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient", "EITHER statement ALONE is sufficient", "Statements (1) and (2) TOGETHER are NOT sufficient"]
        self.questionData["answer"] = self.questionData["options"][ord(self.questionData["answer"]) - ord("A")]

        
        return self.questionData