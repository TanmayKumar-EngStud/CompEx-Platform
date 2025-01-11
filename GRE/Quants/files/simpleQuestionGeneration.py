from GRE.Quants.files.questionComponents import SimpleQuestion
import random
class SimpleQuestionGeneration:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}
    def generate_question(self):
      simpleQuestion = SimpleQuestion(self.llm, self.prompt)
      self.questionData["thread_id"], self.questionData["question"] = simpleQuestion.generate_questionText()
      self.questionData["title"] = simpleQuestion.generate_questionTitle()
      self.questionData["solution"] = simpleQuestion.generate_questionSolution()
      options, answer = simpleQuestion.generate_questionOptions()
      
      self.questionData["answer"] = options[answer]
      option_list = list(options.values())
      random.shuffle(option_list)
      print(f"option_list: {option_list}")
      self.questionData["options"] = option_list
      self.questionData["difficulty"] = int(self.prompt.split(" - ")[2].strip("<>"))
      self.questionData["tag"] = self.prompt.split(" - ")[0].strip("<>").strip("[]").split(",")
      return self.questionData