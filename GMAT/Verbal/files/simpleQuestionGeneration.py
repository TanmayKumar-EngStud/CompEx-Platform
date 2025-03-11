import sys, os, json, re
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from dotenv import load_dotenv
from google import genai

# GMAT.Verbal.files.
from Verbal.files.questionComponents import SimpleQuestion
import random
class SimpleQuestionGeneration:
   def __init__(self, global_state, lock, api_IDX, prompt=None):
      load_dotenv()
      api_key = os.getenv(f"API_{api_IDX}")
      self.llm = genai.Client(api_key = api_key)
      with open(os.path.join(os.path.dirname(__file__), "../System_instructions/GMAT-Verbal-Simple-Questions.txt")) as f:
         self.system_instructions = f.read()

      self.global_state = global_state
      self.lock = lock
      self.prompt = prompt
      self.questionData = {}

   def generate_question(self):
      questionContent = SimpleQuestion(self.llm, self.system_instructions, self.global_state, self.lock, self.prompt)
      self.questionData["type"] = "CR"
      self.questionData["prompt"] = self.prompt
      passages = questionContent.generate_QuestionPassage()

      self.questionData["content"] = {"passages": passages}

      self.questionData["question"] = questionContent.generate_questionText()
      self.questionData["title"] = questionContent.generate_questionTitle()
      options, answer= questionContent.generate_questionOptions()
      self.questionData["answer"] = options[answer]
      options_list = list(options.values())
      random.shuffle(options_list)
      self.questionData["options"] = options_list
      self.questionData["solution"] = questionContent.generate_questionSolution()
      pattern = r'<difficulty_level: (\d+)>'
      difficulty = re.search(pattern, self.prompt)
      if difficulty:
         self.questionData["difficulty"] = int(difficulty.group(1))
      tags = [self.prompt.split(" - ")[0].strip("<>").strip("[]").split(",")[0], self.prompt.split(" - ")[1].strip("<>").strip("[]").split(",")[0], self.prompt.split(" - ")[2].strip("<>").strip("[]").split(",")[0]]
      self.questionData["tag"] = tags

      return self.questionData
   
# s = SimpleQuestionGeneration(prompt= "<psychology> - <CR> - <complete the argument> - <difficulty_level: 5>")
# print(s.generate_question())