from GRE.Quants.files.questionComponents import ParentChildQuestion, SimpleQuestion
import json, re
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
import os
class NumericEntryQuestionGeneration:
   def __init__(self, prompt= None):
      load_dotenv()
      assistant_id = json.load(open(os.path.join(os.path.dirname(__file__), "../../assistant_ids.json"), "r"))["GRE-Quants-Numeric-Entry"]
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
      self.questionData["type"] = "NE"
      self.questionData["prompt"] = self.prompt
      self.questionData["thread_id"] = self.thread_id
      if "graph" in self.prompt.lower() or "table" in self.prompt.lower():
         numericEntryQuestion = ParentChildQuestion(self.llm, self.prompt)
         self.thread_id, content = numericEntryQuestion.generate_questionGraph()
         self.questionData["content"] = content
      numericEntryQuestion = SimpleQuestion(self.llm, self.prompt, self.thread_id)
      self.thread_id, self.questionData["question"] = numericEntryQuestion.generate_questionText()
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