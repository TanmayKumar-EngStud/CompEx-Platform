import json, os
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from GRE.Verbal.files.simpleQuestionGeneration import SimpleQuestionGeneration
from GRE.Verbal.files.parentChildQuestionGeneration import ParentChildQuestionGeneration
from GRE.Verbal.combinations.combination import Combination
load_dotenv()

assistant_id_simple_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GRE-Verbal-Simple-Questions"]
assistant_id_parent_child_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GRE-Verbal-Parent-Child-Questions"]

llm = None

class GRE_V:
    def __init__(self):
       self.combination = Combination()
       self.prompt = self.combination.generate_combination()
       self.llm = None
   
    def generate_questions(self):
       questions = []
       print(f"prompt: {json.dumps(self.prompt, indent=2)}")
       questions.append(self.generate_question(self.prompt, self.llm))
       return questions
    
    def generate_question(self, prompt, llm):
      if ("<rc-" in prompt):
         # print("parent child question generation")
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=assistant_id_parent_child_questions
         )
         parentChildQuestionGeneration = ParentChildQuestionGeneration(llm, prompt)
         
         questionData = parentChildQuestionGeneration.generate_question()
         return questionData
      else:
         # print("simple question generation")
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=assistant_id_simple_questions
         )
         simpleQuestionGeneration = SimpleQuestionGeneration(llm, prompt)
         questionData = simpleQuestionGeneration.generate_question()
         return questionData


# verbal_question_gen = GRE_V()
# verbal_questions = verbal_question_gen.generate_questions()

# print(json.dumps(verbal_questions, indent= 4))