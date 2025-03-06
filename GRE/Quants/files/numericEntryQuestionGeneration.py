# GRE.Quants.files.
from questionComponents import ParentChildQuestion, SimpleQuestion
import json, re
from dotenv import load_dotenv
from google import genai
import os
class NumericEntryQuestionGeneration:
   def __init__(self, prompt= None, api_IDX = 1):
      load_dotenv()
      api_key = os.getenv(f"API_{api_IDX}")
      self.llm = genai.Client(api_key = api_key)
      with open(os.path.join(os.path.dirname(__file__), "../System_instructions/GRE-Quants-Numeric-Entry.txt"), "r") as f:
         self.system_instructions = f.read()
      self.prompt = prompt
      self.questionData = {}

      self.thread_id = None
   
   def generate_question(self):
      self.questionData["type"] = "NE"
      self.questionData["prompt"] = self.prompt
      self.questionData["thread_id"] = self.thread_id
      if "graph" in self.prompt.lower() or "table" in self.prompt.lower():
         numericEntryQuestion = ParentChildQuestion(self.llm, self.system_instructions, self.prompt)
         content = numericEntryQuestion.generate_questionGraph()
         self.questionData["content"] = content
      numericEntryQuestion = SimpleQuestion(self.llm, self.system_instructions, self.prompt)
      self.questionData["question"] = numericEntryQuestion.generate_questionText()
      self.questionData["title"] = numericEntryQuestion.generate_questionTitle()
      self.questionData["solution"], self.questionData["answer"] = numericEntryQuestion.generate_questionSolution(isNE = True)

      try:
            match = re.search(r"<(.*?)>", self.prompt)
            tag = ["Numeric Entry"]
            if match:
                first_content = match.group(1)
                tag.append(first_content)
            self.questionData["tag"] = tag
      except Exception as e:
            print(f"Error: {self.prompt} the length of the prompt is {len(self.prompt.split('-'))}")
            self.questionData["tag"] = ["Numeric Entry"]

      pattern = r'<difficulty-level: (\d+)>'
      match = re.search(pattern, self.prompt)
      self.questionData["difficulty"] = int(match.group(1))

      return self.questionData