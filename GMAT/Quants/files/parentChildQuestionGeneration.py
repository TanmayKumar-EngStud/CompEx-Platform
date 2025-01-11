import random
from GMAT.Quants.files.questionComponents import ParentChildQuestion
class ParentChildQuestionGeneration:
    def __init__(self, llm, prompt, child_prompt= []):
        self.llm = llm
        self.prompt = prompt
        self.child_prompt = child_prompt
        self.questionData = {}
    def generate_question(self):
        questionContent = ParentChildQuestion(self.llm, self.prompt)
        self.questionData["thread_id"], self.questionData["graph/table"] = questionContent.generate_questionGraph()
        self.questionData["title"] = questionContent.generate_parentTitle()
        self.questionData["childQuestions"] = []
        child_question_numbers = len(self.child_prompt) if self.child_prompt else random.randint(2, 4)
        for i in range(child_question_numbers):
            childQuestionData = {}
            childQuestionData["question"] = questionContent.generate_childQuestion(i, self.child_prompt[i] if self.child_prompt else "")
            childQuestionData["title"] = questionContent.generate_childQuestionTitle(i)
            childQuestionData["solution"] = questionContent.generate_childSolution(i)
            options, answer = questionContent.generate_childOptions(i)
            childQuestionData["answer"] = options[answer]
            options_list = list(options.values())
            random.shuffle(options_list)
            childQuestionData["options"] = options_list
            childQuestionData["difficulty"] = int(self.prompt.split(" - ")[2].strip("<>"))
            childQuestionData["tag"] = self.prompt.split(" - ")[0].strip("<>").strip("[]").split(",")
            self.questionData["childQuestions"].append(childQuestionData)
        return self.questionData