import os
import json
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from files.simpleQuestionGeneration import SimpleQuestionGeneration
from files.parentChildQuestionGeneration import ParentChildQuestionGeneration
from files.dataSufficiencyQuestionGeneration import DataSufficiencyQuestionGeneration
from combinations.combination import Combination

load_dotenv()
class GMATQuants:
   def __init__(self):
      combination = Combination()
      self.assistant_id_simple_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Quants-Simple-Questions"]
      self.assistant_id_data_sufficiency_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Quants-Data-Sufficiency-Questions"]
      self.assistant_id_parent_child_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Quants-Parent-Child-Questions"]
      self.prompt = combination.generate_question()
      print(self.prompt)
   def generate_question(self):
      
      if ("data sufficiency" in self.prompt.lower()):
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_data_sufficiency_questions
         )
         dataSufficiencyQuestionGeneration = DataSufficiencyQuestionGeneration(llm, self.prompt)
         
         questionData = dataSufficiencyQuestionGeneration.generate_question()
         return questionData
      elif ("graph" in self.prompt.lower()):
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_parent_child_questions
         )
         parentChildQuestionGeneration = ParentChildQuestionGeneration(llm, self.prompt)
         questionData = parentChildQuestionGeneration.generate_question()
         return questionData
      else:
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_simple_questions
         )
         simpleQuestionGeneration = SimpleQuestionGeneration(llm, self.prompt)
         
         questionData = simpleQuestionGeneration.generate_question()
         return questionData

gmatQuants = GMATQuants()
print(gmatQuants.generate_question())