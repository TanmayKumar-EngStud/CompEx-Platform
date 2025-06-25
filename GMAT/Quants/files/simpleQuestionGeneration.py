import random
import json, os, re
from google import genai
from dotenv import load_dotenv

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter

class SimpleQuestionGeneration:
   def __init__(self, global_state, lock, api_IDX, prompt=None):

      load_dotenv()
      self.global_state = global_state
      self.lock = lock
      api_key = os.getenv(f"API_{api_IDX}")
      self.llm = genai.Client(api_key=api_key)
      with open(os.path.join(os.path.dirname(__file__), "../System_instructions/GMAT-Quants-Simple-Questions.txt"), "r") as f:
         self.system_instructions = f.read()
      self.prompt = prompt
      self.questionData = {}
      self.max_retries = 3

   def _retry_generate(self, func, *args):
      last_error = None
      for attempt in range(self.max_retries):
         try:
            result = func(*args)
            if result:  # If we got any non-None result, return it
               return result
            print(f"Retrying {func.__name__} - attempt {attempt + 1}/{self.max_retries}")
         except Exception as e:
            last_error = str(e)
            print(f"Error in attempt {attempt + 1}: {last_error}")

      # If we get here, all attempts failed
      if last_error:
         print(f"All attempts failed. Last error: {last_error}")
      return None
   
   def generate_question(self):
      try:
         # Create unified component and wrap with GMAT adapter
         component = create_question_component(
            question_type=QuestionType.PROBLEM_SOLVING,
            llm=self.llm,
            system_instructions=self.system_instructions,
            global_state=self.global_state,
            lock=self.lock,
            prompt=self.prompt,
            exam_type=ExamType.GMAT
         )
         questionContent = GMATAdapter.adapt_simple_question(component)
         # Generate question text
         question = questionContent.generate_questionText(self.prompt)
         self.questionData["type"] = "MCQ-Single"
         self.questionData["prompt"] = self.prompt
         self.questionData["question"] = question

         # Generate title
         title = questionContent.generate_questionTitle()
         self.questionData["title"] = title if title else "GMAT Quants Question"

         # Generate solution
         solution = questionContent.generate_questionSolution()
         self.questionData["solution"] = solution if solution else "Solution not available"

         # Generate options and answer
         options, answer = questionContent.generate_questionOptions()
         if options:
            options_list = list(options.values())
            random.shuffle(options_list)
            self.questionData["options"] = options_list
            self.questionData["answer"] = options[answer] if answer in options else options_list[0]
         else:
            self.questionData["options"] = ["A", "B", "C", "D"]
            self.questionData["answer"] = "A"
         
         # Set difficulty and tags
         pattern = r'<difficulty_level: (\d+)>'
         difficulty = re.search(pattern, self.prompt)
         if difficulty:
            self.questionData["difficulty"] = int(difficulty.group(1))
         else:
            self.questionData["difficulty"] = -1
            
         tags = [self.prompt.split(" - ")[x].strip("<>") for x in [0, 1, 2, 3]]
         self.questionData["tags"] = [re.sub(r'\([^)]*\)', '', tag) for tag in tags]
         return self.questionData
         
      except Exception as e:
         raise Exception(f"Error in generate_question: {str(e)}")
         
