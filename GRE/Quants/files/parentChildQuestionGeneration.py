from GRE.Quants.files.questionComponents import ParentChildQuestion
import json
import random
class ParentChildQuestionGeneration:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}
        self.thread_id = None
    def generate_question(self):
        parentChildQuestion = ParentChildQuestion(self.llm, self.prompt)
        self.thread_id, self.questionData["graph/table"] = parentChildQuestion.generate_questionGraph()

        self.questionData["title"] = parentChildQuestion.generate_parentTitle()
        number_of_child_questions = random.randint(2,4)
        self.questionData["childQuestions"] = []
        for i in range(number_of_child_questions):
            childQuestionData = {}
            childQuestionData["question"] = parentChildQuestion.generate_childQuestion(i)
            childQuestionData["number"] = i
            childQuestionData["title"] = parentChildQuestion.generate_childQuestionTitle(i)
            childQuestionData["solution"] = parentChildQuestion.generate_childSolution(i)
            options, answer = parentChildQuestion.generate_childOptions(i)
            childQuestionData["answer"] = options[answer]
            option_list = list(options.values())
            random.shuffle(option_list)
            childQuestionData["options"] = option_list
            self.questionData["childQuestions"].append(childQuestionData)
        self.questionData["difficulty"] = int(self.prompt.split(" - ")[2].strip("<>"))
        self.questionData["tag"] = ["PS", self.prompt.split(" - ")[3].strip("<>").strip("[]").split(",")]
        return self.questionData