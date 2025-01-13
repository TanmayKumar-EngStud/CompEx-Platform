import json, os
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from GMAT.Verbal.files.simpleQuestionGeneration import SimpleQuestionGeneration
from GMAT.Verbal.files.parentChildQuestionGeneration import ParentChildQuestionGeneration
from GMAT.Verbal.combinations.combination import Combination
load_dotenv()

class GMAT_V:
   def __init__(self):
      combination = Combination()
      self.prompt = combination.generate_combination()
      self.assistant_id_simple_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Verbal-Simple-Questions"]
      self.assistant_id_parent_child_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Verbal-Parent-Child-Questions"]
   def generate_question(self):
      prompt = self.prompt
      print(f"GMAT Verbal: generating parent child question")
      if("rc" in prompt.lower()):
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_parent_child_questions
         )
         parentChildQuestionGeneration = ParentChildQuestionGeneration(llm, prompt)
         questionData = parentChildQuestionGeneration.generate_question()
         questionData["prompt"] = prompt
         return questionData
      else:
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=self.assistant_id_simple_questions
         )
         print("GMAT Verbal: generating simple question")
         simpleQuestionGeneration = SimpleQuestionGeneration(llm, prompt)
         questionData = simpleQuestionGeneration.generate_question()
         questionData["prompt"] = prompt
         return questionData
      
# verbalQuestionGeneration = GMAT_V()
# questionData = verbalQuestionGeneration.generate_question()
# print(json.dumps(questionData, indent=4))
