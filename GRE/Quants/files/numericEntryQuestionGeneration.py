from GRE.Quants.files.questionComponents import ParentChildQuestion, SimpleQuestion
import json, random, re

class NumericEntryQuestionGeneration:
   def __init__(self, llm, prompt):
      self.llm = llm
      self.prompt = prompt
      self.questionData = {}

      self.thread_id = None
   
   def generate_question(self):
      if "graph" in self.prompt.lower() or "table" in self.prompt.lower():
         numericEntryQuestion = ParentChildQuestion(self.llm, self.prompt)
         self.thread_id, self.questionData["graph/table"] = numericEntryQuestion.generate_questionGraph()

      numericEntryQuestion = SimpleQuestion(self.llm, self.prompt, self.thread_id)
      self.thread_id, self.questionData["question"] = numericEntryQuestion.generate_questionText()
      self.questionData["title"] = numericEntryQuestion.generate_questionTitle()
      self.questionData["solution"], self.questionData["answer"] = numericEntryQuestion.generate_questionSolution()
      self.questionData["difficulty"] = int(self.prompt.split(" - ")[2].strip("<>"))
      tag = re.sub(r'\([^)]*\)', '', self.prompt.split(" - ")[1].strip("<>"))
      tag = tag.strip()
      
      self.questionData["tag"] = ["numeric entry", tag]
      return self.questionData

