import random
from files.questionComponents import TA

class Generate_TA:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}
    def generate_TA(self):
        ta = TA(self.llm, self.prompt)
        self.questionData["thread_id"], self.questionData["table"] = ta.generate_QuestionTable()
        self.questionData["question"] = ta.generate_QuestionText()
        self.questionData["title"] = ta.generate_QuestionTitle()
        self.questionData["solution"] = ta.generate_QuestionSolution()
        options, correct_option = ta.generate_QuestionOptions()
        option_list = list(options.values())
        random.shuffle(option_list)
        self.questionData["options"] = option_list
        self.questionData["answer"] = options[correct_option]
        self.questionData["tags"] = ["TA", self.prompt.split("-")[2].strip().strip('<>').strip()]
        self.questionData["difficulty"] = self.prompt.split("-")[3].strip().strip('<>').strip()
        return self.questionData