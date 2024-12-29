import random
from files.questionComponents import GI 

class Generate_GI:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}
    def generate_GI(self):
        gi = GI(self.llm, self.prompt)
        self.questionData["thread_id"], self.questionData["graphs"] = gi.generate_questionGraph()
        self.questionData["question"] = gi.generate_questionText()
        self.questionData["title"] = gi.generate_questionTitle()
        self.questionData["solution"] = gi.generate_questionSolution()
        options, correct_option = gi.generate_questionOptions()
        self.questionData["options"] = random.shuffle(list(options.values()))
        self.questionData["answer"] = options[correct_option]
        self.questionData["tags"] = ["GI", self.prompt.split("-")[2].strip().strip('<>').strip()]
        self.questionData["difficulty"] = self.prompt.split("-")[3].strip().strip('<>').strip()
        return self.questionData