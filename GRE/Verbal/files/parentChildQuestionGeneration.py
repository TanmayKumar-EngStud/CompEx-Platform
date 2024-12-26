from files.questionComponents import ParentChildQuestion
import random
class ParentChildQuestionGeneration:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}

    def generate_question(self, child_prompts=[]):
        parentChildQuestion = ParentChildQuestion(self.llm, self.prompt)
        self.questionData["passages"] = parentChildQuestion.generate_passages()
        self.questionData["title"] = parentChildQuestion.generate_parentTitle()
        child_question_numbers = len(child_prompts) if child_prompts else random.randint(2, 4)
        self.questionData["childQuestions"] = []
        for i in range(child_question_numbers):
            childQuestionData = {}
            childQuestionData["question"] = parentChildQuestion.generate_childQuestion(i, child_prompts[i])
            childQuestionData["options"] = parentChildQuestion.generate_childOptions(i)
            childQuestionData["solution"], childQuestionData["answer"] = parentChildQuestion.generate_childSolution(i)
            self.questionData["childQuestions"].append(childQuestionData)
        return self.questionData