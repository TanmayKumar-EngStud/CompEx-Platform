from GRE.Verbal.files.questionComponents import SimpleQuestion
import random
class SimpleQuestionGeneration:
    def __init__(self, llm, prompt):
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
      questionContent = SimpleQuestion(self.llm)
      self.questionData["thread_id"], self.questionData["question"] = questionContent.generate_questionText(self.prompt)
      self.questionData["title"] = questionContent.generate_questionTitle()
      num_options = 0
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
      self.questionData["difficulty"] = int(self.prompt.split(" - ")[3].strip("<>"))
      self.questionData["tag"] = self.prompt.split(" - ")[2].strip("<>").strip("[]").split(",")
      return self.questionData