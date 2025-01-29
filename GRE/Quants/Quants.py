import json, os
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable

from GRE.Quants.combinations.combination import Combination

from GRE.Quants.files.simpleQuestionGeneration import SimpleQuestionGeneration
from GRE.Quants.files.dataSufficiencyQuestionGeneration import DataSufficiencyQuestionGeneration
from GRE.Quants.files.parentChildQuestionGeneration import ParentChildQuestionGeneration
from GRE.Quants.files.numericEntryQuestionGeneration import NumericEntryQuestionGeneration
load_dotenv()

class GRE_Q:
   def __init__(self):
      self.combination = Combination()
      self.prompts = self.combination.generate_combination()
      self.assistant_id_simple_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GRE-Quants-Simple-Questions"]
      self.assistant_id_parent_child_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GRE-Quants-Parent-Child-Questions"]
      self.assistant_id_data_sufficiency_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GRE-Quants-Data-Sufficiency-Questions"]
      self.assistant_id_numeric_entry_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GRE-Quants-Numeric-Entry"]
   def generate_questions(self):
      questions = []
      for prompt in self.prompts:
         questions.append(self.generate_question(prompt))
      return questions

   def generate_question(self, prompt):
      llm = None
      if ("data sufficiency" in prompt.lower()):

         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_data_sufficiency_questions
         )
         data_sufficiency_question_generation = DataSufficiencyQuestionGeneration(llm, prompt)
         try:
            questionData = data_sufficiency_question_generation.generate_question()
            questionData["prompt"] = prompt
            return questionData
         except Exception as e:
            print(f"GRE Quants, Data Sufficiency, Error: {e}")
            return {}

      elif ("graph" in prompt.lower() or "table" in prompt.lower()):
         # Parent Child Question Generation
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_parent_child_questions
         )
         try:
            parentChildQuestionGeneration = ParentChildQuestionGeneration(llm, prompt)
            questionData = parentChildQuestionGeneration.generate_question()
            questionData["prompt"] = prompt
            return questionData
         except Exception as e:
            print(f"GRE Quants, Parent Child, Error: {e}")
            return {}

      elif "problem solving" in prompt.lower():
         # Simple Question Generation
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_simple_questions
         )
         simpleQuestionGeneration = SimpleQuestionGeneration(llm, prompt)
         try:
            questionData = simpleQuestionGeneration.generate_question()
            questionData["prompt"] = prompt
            return questionData
         except Exception as e:
            print(f"GRE Quants, Simple, Error: {e}")
            return {}

      if "numeric entry" in prompt.lower():
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_numeric_entry_questions
         )
         numericEntryQuestionGeneration = NumericEntryQuestionGeneration(llm, prompt)
         try:
            questionData = numericEntryQuestionGeneration.generate_question()
            questionData["prompt"] = prompt
            return questionData
         except Exception as e:
            print(f"GRE Quants, Numeric Entry, Error: {e}")
            return {}
      return None



# quantsQuestionGeneration = GRE_Q()
# print(f"generating questions")
# questions = quantsQuestionGeneration.generate_questions()
# print(f"questions generated")
# print(json.dumps(questions, indent=4))