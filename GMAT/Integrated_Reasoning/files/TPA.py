from GMAT.Integrated_Reasoning.files.questionComponents import TPA
import random
class Generate_TPA:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}
    def generate_TPA(self):
        tpa = TPA(self.llm, self.prompt)
        self.questionData["thread_id"], self.questionData["part1"], self.questionData["part2"], self.questionData["question"], self.questionData["type"] = tpa.generate_QuestionText()
        self.questionData["title"] = tpa.generate_QuestionTitle()
        
        if("requires math calculation" in self.questionData["type"].lower()):
            self.questionData["solution"] = tpa.generate_QuestionSolution()
            options, answer = tpa.generate_QuestionOptions()
        else:
            options, answer = tpa.generate_QuestionOptions()
            self.questionData["solution"] = tpa.generate_QuestionSolution()
        option_list = list(options.values())
        random.shuffle(option_list)
        self.questionData["options"] = option_list
        self.questionData["answer"]= options[answer]
        self.questionData["tags"] = ["TPA", self.prompt.split("-")[2].strip().strip('<>').strip()]
        return self.questionData