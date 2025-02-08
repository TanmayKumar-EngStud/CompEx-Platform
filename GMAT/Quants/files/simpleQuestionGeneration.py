import random
from GMAT.Quants.files.questionComponents import SimpleQuestion
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from dotenv import load_dotenv
import json, os, re

class SimpleQuestionGeneration:
   def __init__(self, prompt=None):
      load_dotenv()
      assistant_id = json.load(open(os.path.join(os.path.dirname(__file__), "../../assistant_ids.json"), "r"))["GMAT-Quants-Simple-Questions"]
      openai_api_key = os.getenv("OPENAI_API_KEY")
      if not openai_api_key:
         raise Exception("OPENAI_API_KEY is not set in the environment variables")
      llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=openai_api_key,
            assistant_id=assistant_id
      )
      self.llm = llm
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
         questionContent = SimpleQuestion(self.llm)
         
         # Generate question text
         thread_id, question = questionContent.generate_questionText(self.prompt)
         if not thread_id or not question:
            raise Exception("Failed to generate valid question text")
         self.questionData["type"] = "MCQ-Single"
         self.questionData["prompt"] = self.prompt
         self.questionData["thread_id"] = thread_id
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
         
