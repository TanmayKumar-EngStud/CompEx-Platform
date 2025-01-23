import json, os
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from GMAT.Integrated_Reasoning.files.GI import Generate_GI
from GMAT.Integrated_Reasoning.files.MSR import Generate_MSR
from GMAT.Integrated_Reasoning.files.TA import Generate_TA
from GMAT.Integrated_Reasoning.files.TPA import Generate_TPA
from GMAT.Integrated_Reasoning.combinations.combiantion import Combination
load_dotenv()

assistant_id_graphic_interpretation = json.load(open(os.path.join(os.path.dirname(__file__), '../assistant_ids.json'), 'r'))['Graphic-Interpretation']
assistant_id_multi_source_reasoning = json.load(open(os.path.join(os.path.dirname(__file__), '../assistant_ids.json'), 'r'))['Multi-Source-Reasoning']
assistant_id_table_analysis = json.load(open(os.path.join(os.path.dirname(__file__), '../assistant_ids.json'), 'r'))['Table-Analysis']
assistant_id_two_part_analysis = json.load(open(os.path.join(os.path.dirname(__file__), '../assistant_ids.json'), 'r'))['Two-Part-Analysis']

class GMAT_IR:
   def __init__(self):
      
      self.combination = Combination()
      self.combination_prompt = self.combination.generate_combination()

   def generate_questions(self):
      questions = []
      for prompt in self.combination_prompt:
         question = self.generate_Question(prompt)
         questions.append(question)
      return questions

   def generate_Question(self, prompt):
      if("graphic interpretation" in prompt.lower()):

         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=assistant_id_graphic_interpretation
         )
         gi = Generate_GI(llm, prompt)
         gi_question = gi.generate_GI()
         gi_question["prompt"] = prompt
         return gi_question

      elif("multi source reasoning" in prompt.lower()):
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=assistant_id_multi_source_reasoning
         )
         msr = Generate_MSR(llm, prompt)
         msr_question = msr.generate_MSR()
         msr_question["prompt"] = prompt
         return msr_question

      elif("table analysis" in prompt.lower()):
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=assistant_id_table_analysis
         )
         ta = Generate_TA(llm, prompt)
         ta_question = ta.generate_TA()
         ta_question["prompt"] = prompt
         return ta_question
      elif("two part analysis" in prompt.lower()):
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=assistant_id_two_part_analysis
         )
         tpa = Generate_TPA(llm, prompt)
         tpa_question = tpa.generate_TPA()
         tpa_question["prompt"] = prompt
         return tpa_question

# ir = GMAT_IR()
# print(f"generating questions...")
# questions = ir.generate_IR()
# print(f"Generated Questions:- \n{json.dumps(questions, indent=2)}\n\n")
# print(f"questions generated")