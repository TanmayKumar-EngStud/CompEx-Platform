from files.questionComponents import QuestionText, QuestionTitle, QuestionSolution, QuestionOptions

class SimpleQuestionGeneration:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}

    def generate_question(self):
      questionText = QuestionText(self.llm)
      self.questionData["thread_id"], self.questionData["question"] = questionText.generate_questionText(self.prompt)

      questionTitle = QuestionTitle(self.llm, self.questionData["thread_id"])
      self.questionData["title"] = questionTitle.generate_questionTitle()

      questionSolution = QuestionSolution(self.llm, self.questionData["thread_id"])
      self.questionData["solution"], self.questionData["answer"] = questionSolution.generate_questionSolution()

      questionOptions = QuestionOptions(self.llm, self.questionData["thread_id"])
      self.questionData["options"] = questionOptions.generate_questionOptions(3)
      self.questionData["difficulty"] = int(self.prompt.split(" - ")[1].strip("<>"))
      self.questionData["tag"] = self.prompt.split(" - ")[0].strip("<>").strip("[]").split(",")
      return self.questionData