import random
from files.questionComponents import MSR

class Generate_MSR:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}
    def generate_MSR(self):
        msr = MSR(self.llm, self.prompt)
        self.questionData["sources"] = []
        for source_index in range(1, 4):
            source = {}
            self.questionData["thread_id"], source = msr.generate_SourceInfo(source_index)
            self.questionData["sources"].append(source)
        self.questionData["questions"] = []
        for source_index in range(1, 4):
            question = {}
            question["question"] = msr.generate_QuestionText(source_index)
            question["title"] = msr.generate_QuestionTitle(source_index)
            question["solution"] = msr.generate_QuestionSolution(source_index)
            options, correct_option = msr.generate_QuestionOptions(source_index)
            option_list = list(options.values())
            random.shuffle(option_list)
            question["options"] = option_list

            question["answer"] = options[correct_option]
            self.questionData["questions"].append(question)

        self.questionData["tags"] = ["MSR", self.prompt.split("-")[2].strip().strip('<>').strip()]
        self.questionData["difficulty"] = self.prompt.split("-")[3].strip().strip('<>').strip()
        return self.questionData