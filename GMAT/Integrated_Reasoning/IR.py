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
      self.max_retries = 3

   def generate_questions(self):
      questions = []
      for prompt in self.combination_prompt:
         question = self.generate_Question(prompt)
         questions.append(question)
      return questions

   def _generate_with_retry(self, generator_func, prompt, question_type):
      """Helper method to handle retries for question generation"""
      for attempt in range(self.max_retries):
         try:
            question = generator_func()
            question["prompt"] = prompt

            print(f"✅ {question_type}: Successfully generated")
            return question
         except Exception as e:
            if attempt < self.max_retries - 1:
               print(f"⚠️  {question_type}: Attempt {attempt + 1} failed, retrying...")
               print(f"   Error: {str(e)}")
            else:
               print(f"❌ {question_type}: Failed after {self.max_retries} attempts")
               print(f"   Error: {str(e)}")
               return {
                  "error": f"Failed to generate {question_type} question after {self.max_retries} attempts: {str(e)}",
                  "prompt": prompt,
                  "question_type": question_type
               }

   def generate_Question(self, prompt):
      if("graphic interpretation" in prompt.lower()):
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=assistant_id_graphic_interpretation
         )
         gi = Generate_GI(llm, prompt)
         return self._generate_with_retry(
            generator_func=gi.generate_GI,
            prompt=prompt,
            question_type="Graphic Interpretation"
         )

      elif("multi source reasoning" in prompt.lower()):
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=assistant_id_multi_source_reasoning
         )
         msr = Generate_MSR(llm, prompt)
         return self._generate_with_retry(
            generator_func=msr.generate_MSR,
            prompt=prompt,
            question_type="Multi Source Reasoning"
         )

      elif("table analysis" in prompt.lower()):
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=assistant_id_table_analysis
         )
         ta = Generate_TA(llm, prompt)
         return self._generate_with_retry(
            generator_func=ta.generate_TA,
            prompt=prompt,
            question_type="Table Analysis"
         )
      elif("two part analysis" in prompt.lower()):
         llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=assistant_id_two_part_analysis
         )
         tpa = Generate_TPA(llm, prompt)
         return self._generate_with_retry(
            generator_func=tpa.generate_TPA,
            prompt=prompt,
            question_type="Two Part Analysis"
         )

# ir = GMAT_IR()
# print(f"generating questions...")
# questions = ir.generate_IR()
# print(f"Generated Questions:- \n{json.dumps(questions, indent=2)}\n\n")
# print(f"questions generated")