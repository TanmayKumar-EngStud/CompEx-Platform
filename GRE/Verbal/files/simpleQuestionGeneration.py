from Verbal.files.questionComponents import SimpleQuestion
import random, os, json, re
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable

class SimpleQuestionGeneration:
    def __init__(self, llm=None, prompt=None):
        load_dotenv()
        assistant_id = json.load(open(os.path.join(os.path.dirname(__file__), "../../assistant_ids.json"), "r"))["GRE-Verbal-Simple-Questions"]
        if llm is None:
            llm = OpenAIAssistantRunnable(
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
                assistant_id=assistant_id
            )
        self.llm = llm
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
      questionContent = SimpleQuestion(self.llm, self.prompt)
      self.questionData["thread_id"], self.questionData["question"] = questionContent.generate_questionText()
      self.questionData["title"] = questionContent.generate_questionTitle()
      num_options = 6
      if "tc-1" in self.prompt:
         num_options = 6
      elif "tc-2" in self.prompt:
         num_options = 8
      elif "tc-3" in self.prompt:
         num_options = 9
      options, answer = questionContent.generate_questionOptions(num_options)
      if(isinstance(answer, str)):
         self.questionData["answer"] = answer
      else:
         answers = []
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
      prompt_parts = self.prompt.split("-")
      theme = prompt_parts[0].strip().strip("<>").lower()
      question_type = prompt_parts[1].strip("<>").lower()
      try:
         self.questionData["tags"] = [theme, question_type]
      except Exception as e:
         print(f"Error: {self.prompt} the length of the prompt is {len(self.prompt.split('-'))}")
         self.questionData["tags"] = ["Simple", "Simple"]
      
      return self.questionData