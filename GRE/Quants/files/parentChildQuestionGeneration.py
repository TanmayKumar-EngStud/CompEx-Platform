from files.questionComponents import QuestionGraph, ChildQuestionText, QuestionTitle, ChildQuestionSolution, QuestionOptions
import json
import random
class ParentChildQuestionGeneration:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}
        self.thread_id = None
    def generate_question(self):
        questionGraph = QuestionGraph(self.llm, self.prompt)
        self.thread_id, self.questionData["graph/table"] = questionGraph.generate_questionGraph()
        self.questionData["thread_id"] = self.thread_id
        questionTitle = QuestionTitle(self.llm, self.thread_id)
        self.questionData["title"] = questionTitle.generate_questionTitle()
        number_of_child_questions = random.randint(2,4)
        self.questionData["childQuestions"] = []
        for i in range(number_of_child_questions):
            childQuestionData = {}
            childQuestionText = ChildQuestionText(self.llm, "",self.thread_id)
            childQuestionData["number"] = i
            childQuestionData["question"] = childQuestionText.generate_childQuestionText(i)
            childQuestionTitle = QuestionTitle(self.llm, self.thread_id)
            childQuestionData["title"] = childQuestionTitle.generate_questionTitle()
            childQuestionSolution = ChildQuestionSolution(self.llm, self.thread_id)
            childQuestionData["solution"], childQuestionData["answer"] = childQuestionSolution.generate_childQuestionSolution(i+1)
            childQuestionOptions = QuestionOptions(self.llm, self.thread_id)
            childQuestionData["options"] = childQuestionOptions.generate_questionOptions()

            self.questionData["childQuestions"].append(childQuestionData)
        return self.questionData