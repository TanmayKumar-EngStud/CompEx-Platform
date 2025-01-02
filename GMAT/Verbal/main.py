import os
import json
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from files.simpleQuestionGeneration import SimpleQuestionGeneration
from files.parentChildQuestionGeneration import ParentChildQuestionGeneration
from combinations.combination import Combination
load_dotenv()

class VerbalQuestionGeneration:
   def __init__(self):
      combination = Combination()
      self.prompt = combination.generate_combination()
      self.assistant_id_simple_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Verbal-Simple-Questions"]
      self.assistant_id_parent_child_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Verbal-Parent-Child-Questions"]
   def generate_question(self):
      prompt = self.prompt
      print(prompt)
      if("rc" in prompt.lower()):
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_parent_child_questions
         )
         parentChildQuestionGeneration = ParentChildQuestionGeneration(llm, prompt)
         questionData = parentChildQuestionGeneration.generate_question()
         print("Parent Child Question Generation")
         return questionData
      else:
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_simple_questions
         )
         simpleQuestionGeneration = SimpleQuestionGeneration(llm, prompt)
         questionData = simpleQuestionGeneration.generate_question()
         print("Simple Question Generation")
         return questionData
      
verbalQuestionGeneration = VerbalQuestionGeneration()
questionData = verbalQuestionGeneration.generate_question()
print(json.dumps(questionData, indent=4))
