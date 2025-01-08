import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from files.simpleQuestionGeneration import SimpleQuestionGeneration
from files.parentChildQuestionGeneration import ParentChildQuestionGeneration
from files.dataSufficiencyQuestionGeneration import DataSufficiencyQuestionGeneration
from combinations.combination import Combination

load_dotenv()
class GMAT_Q:
   def __init__(self):
      combination = Combination()
      self.assistant_id_simple_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Quants-Simple-Questions"]
      self.assistant_id_data_sufficiency_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Quants-Data-Sufficiency-Questions"]
      self.assistant_id_parent_child_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Quants-Parent-Child-Questions"]
      self.prompts = combination.generate_combination()
      print(self.prompts)
   def generate_questions(self):
      questions = []
      for prompt in self.prompts:
         question = self.generate_question(prompt)
         questions.append(question)
      return questions
   def generate_question(self, prompt):
      
      if ("data sufficiency" in prompt.lower()):
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_data_sufficiency_questions
         )
         dataSufficiencyQuestionGeneration = DataSufficiencyQuestionGeneration(llm, prompt)
         questionData = dataSufficiencyQuestionGeneration.generate_question()
         return questionData
      elif ("graph" in prompt.lower()):
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_parent_child_questions
         )
         parentChildQuestionGeneration = ParentChildQuestionGeneration(llm, prompt)
         questionData = parentChildQuestionGeneration.generate_question()
         return questionData
      else:
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_simple_questions
         )
         simpleQuestionGeneration = SimpleQuestionGeneration(llm, prompt)
         questionData = simpleQuestionGeneration.generate_question()
         return questionData

# gmatQuants = GMAT_Q()
# print(f"generating questions...")
# questions = gmatQuants.generate_questions()
# print(f"questions generated")
# print(f"questions:- \n{json.dumps(questions, indent=2)}\n\n")