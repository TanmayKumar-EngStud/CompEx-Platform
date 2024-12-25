from files.questionComponents import SimpleQuestion

class SimpleQuestionGeneration:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}

    def generate_question(self):
      questionContent = SimpleQuestion(self.llm)
      self.questionData["thread_id"], self.questionData["question"] = questionContent.generate_questionText(self.prompt)
      self.questionData["title"] = questionContent.generate_questionTitle()
      self.questionData["options"] = questionContent.generate_questionOptions(3)
      self.questionData["solution"], self.questionData["answer"] = questionContent.generate_questionSolution()
      self.questionData["difficulty"] = int(self.prompt.split(" - ")[2].strip("<>"))
      self.questionData["tag"] = self.prompt.split(" - ")[0].strip("<>").strip("[]").split(",")
      return self.questionData