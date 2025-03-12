# GRE.Verbal.files.
from GRE.Verbal.files.questionComponents import SimpleQuestion
import random, os, json, re
from dotenv import load_dotenv
from google import genai

class SimpleQuestionGeneration:
    def __init__(self, global_state, lock, api_IDX, prompt):
        load_dotenv()
        self.global_state = global_state
        self.lock = lock
        api_key = os.getenv(f"API_{api_IDX}")
        self.llm = genai.Client(api_key = api_key)
        with open(os.path.join(os.path.dirname(__file__), "../System_instructions/GRE-Verbal-Simple-Questions.txt"), "r") as f:
            self.system_instructions = f.read()
        if "SE" in prompt:
            with open(os.path.join(os.path.dirname(__file__), "../System_instructions/GRE-Verbal-SE.txt"), "r") as f:
                self.system_instructions = f.read()
        self.prompt = prompt
        self.questionData = {}

    def shuffle_options(self,options):
        option_list = []
        if isinstance(options, dict):
            # Shuffle the values of the dictionary
            option_list = list(options.values())
            random.shuffle(option_list)
        elif isinstance(options, list):
            # Shuffle values of each inner dictionary and convert to list of lists
            for inner_dict in options:
                shuffled_values = list(inner_dict.values())
                random.shuffle(shuffled_values)
                option_list.append(shuffled_values)
        return option_list

    def generate_question(self):
      questionContent = SimpleQuestion(self.llm, self.system_instructions, self.global_state, self.prompt, self.lock)
      self.questionData["prompt"] = self.prompt
      self.questionData["question"] = questionContent.generate_questionText()

      self.questionData["title"] = questionContent.generate_questionTitle()

      num_options = 6
      if "tc-1" in self.prompt.lower():
         self.questionData["type"] = "TC-1"
         num_options = 6
      elif "tc-2" in self.prompt.lower():
         self.questionData["type"] = "TC-2"
         num_options = 8
      elif "tc-3" in self.prompt.lower():
         self.questionData["type"] = "TC-3"
         num_options = 12
      elif "se" in self.prompt.lower():
         self.questionData["type"] = "SE"
         num_options = 6
      options, answer = questionContent.generate_questionOptions(num_options)
      # print(f"received options:\n{options}\nanswer:\n{answer}\nfor prompt:{self.prompt}\n\n ")
      if(isinstance(answer, str)):
         self.questionData["answer"] = options[answer]
      else:
         answers = []
         if "<se>" in self.prompt.lower():

            answers.append(options[answer[0]])
            answers.append(options[answer[1]])
         else:
            i=0
            for ans in answer:
               answers.append(options[i][ans])
               i+=1
         self.questionData["answer"] = answers
      self.questionData["options"] = self.shuffle_options(options)

      self.questionData["solution"] = questionContent.generate_questionSolution()

      pattern = r'<difficulty-level: (\d+)>'
      match = re.search(pattern, self.prompt)
      self.questionData["difficulty"] = int(match.group(1))

      
      # Extract theme and type as tags
      prompt_parts = self.prompt.split(" - ")
      theme = prompt_parts[0].strip().strip("<>").lower()
      question_type = prompt_parts[1].strip("<>").lower()
      try:
         self.questionData["tags"] = [theme, question_type]
      except Exception as e:
         print(f"Error: {self.prompt} the length of the prompt is {len(self.prompt.split('-'))}")
         self.questionData["tags"] = ["Simple"]
      

      return self.questionData