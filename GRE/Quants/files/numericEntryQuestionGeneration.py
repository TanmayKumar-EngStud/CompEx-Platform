from Quants.files.questionComponents import ParentChildQuestion, SimpleQuestion
import json, random, re
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
import os
class NumericEntryQuestionGeneration:
   def __init__(self, llm= None, prompt= None):
      load_dotenv()
      assistant_id = json.load(open(os.path.join(os.path.dirname(__file__), "../../assistant_ids.json"), "r"))["GRE-Quants-Numeric-Entry"]
      if llm is None:
            llm = OpenAIAssistantRunnable(
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
                assistant_id=assistant_id
            )
      self.llm = llm
      self.prompt = prompt
      self.questionData = {}

      self.thread_id = None
   
   def generate_question(self):
      if "graph" in self.prompt.lower() or "table" in self.prompt.lower():
         numericEntryQuestion = ParentChildQuestion(self.llm, self.prompt)
         self.thread_id, self.questionData["graph/table"] = numericEntryQuestion.generate_questionGraph()

      numericEntryQuestion = SimpleQuestion(self.llm, self.prompt, self.thread_id)
      self.thread_id, self.questionData["question"] = numericEntryQuestion.generate_questionText()
      self.questionData["title"] = numericEntryQuestion.generate_questionTitle()
      self.questionData["solution"], self.questionData["answer"] = numericEntryQuestion.generate_questionSolution()
      
      pattern = r'<difficulty-level: (\d+)>'
      match = re.search(pattern, self.prompt)
      self.questionData["difficulty"] = int(match.group(1))
      try:
         tag = re.sub(r'\([^)]*\)', '', self.prompt.split("-")[1].strip("<>"))
         tag = tag.strip()
      except Exception as e:
         print(f"Error: {self.prompt} the length of the prompt is {len(self.prompt.split('-'))}")
         tag = "numeric entry"
      
      self.questionData["tag"] = ["numeric entry", tag]
      return self.questionData

