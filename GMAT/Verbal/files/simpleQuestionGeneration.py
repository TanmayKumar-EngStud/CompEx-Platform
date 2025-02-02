import sys, os, json, re
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable


from Verbal.files.questionComponents import SimpleQuestion
import random
class SimpleQuestionGeneration:
   def __init__(self, prompt=None):
      load_dotenv()
      assistant_id = json.load(open(os.path.join(os.path.dirname(__file__), "../../assistant_ids.json"), "r"))["GMAT-Verbal-Simple-Questions"]
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

   def generate_question(self):
      questionContent = SimpleQuestion(self.llm, self.prompt)
      self.questionData["prompt"] = self.prompt
      result = questionContent.generate_QuestionPassage()
      if not result or result == ("", []):
         raise Exception("Failed to generate question passage")
      
      thread_id, passages = result
      self.questionData["thread_id"] = thread_id
      self.questionData["passage"] = passages

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