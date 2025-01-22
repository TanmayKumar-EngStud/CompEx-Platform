import random
from GMAT.Integrated_Reasoning.files.questionComponents import TA

class Generate_TA:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}
    def generate_TA(self):
        ta = TA(self.llm, self.prompt)
        self.questionData["thread_id"], self.questionData["tables"] = ta.generate_QuestionTable()
        self.questionData["question"] = ta.generate_QuestionText()
        self.questionData["title"] = ta.generate_QuestionTitle()
        self.questionData["solution"] = ta.generate_QuestionSolution()
        options, answers = ta.generate_QuestionOptions()
        option_list = list(options.values())
        random.shuffle(option_list)
        self.questionData["options"] = option_list
        self.questionData["answer"]= {options[key]: answers[key] for key in options}
        self.questionData["tags"] = ["TA", self.prompt.split("-")[2].strip().strip('<>').strip()]
        self.questionData["difficulty"] = int(self.prompt.split("-")[4].strip().strip('<>').strip())
        return self.questionData
