from files.questionComponents import SimpleQuestion

class SimpleQuestionGeneration:
   def __init__(self, llm, prompt):
      self.llm = llm
      self.prompt = prompt
      self.questionData = {}

   def generate_question(self):
      questionContent = SimpleQuestion(self.llm, self.prompt)
      if("sentence correction" in self.prompt.lower()):
         self.questionData["thread_id"], self.questionData["question"] = questionContent.generate_questionText()
      else:
         self.questionData["thread_id"], self.questionData["passage"], self.questionData["question"] = questionContent.generate_questionText()
      self.questionData["title"] = questionContent.generate_questionTitle()
      self.questionData["options"] = questionContent.generate_questionOptions()
      self.questionData["solution"], self.questionData["answer"] = questionContent.generate_questionSolution()
      self.questionData["difficulty"] = int(self.prompt.split(" - ")[3].strip("<>"))
      tags = [self.prompt.split(" - ")[0].strip("<>").strip("[]").split(",")[0], self.prompt.split(" - ")[1].strip("<>").strip("[]").split(",")[0], self.prompt.split(" - ")[2].strip("<>").strip("[]").split(",")[0]]
      self.questionData["tag"] = tags

      return self.questionData