from GRE.Quants.files.questionComponents import SimpleQuestion
import random
class SimpleQuestionGeneration:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}

    def getTagAtIndex(self, indexes):
        tags = []
        for index in indexes:
            tags.extend([x.strip() for x in self.prompt.split(" - ")[index].strip("<>").strip("[]").split(",")])
        return tags

    def generate_question(self):
        questionContent = SimpleQuestion(self.llm, self.prompt)
        self.questionData["thread_id"], self.questionData["question"] = questionContent.generate_questionText()
        self.questionData["title"] = questionContent.generate_questionTitle()
        self.questionData["solution"] = questionContent.generate_questionSolution()
        options, answer = questionContent.generate_questionOptions()
        options_list = list(options.values())
        random.shuffle(options_list)
        self.questionData["options"] = options_list
        self.questionData["answer"] = options[answer]
        self.questionData["difficulty"] = int(self.prompt.split(" - ")[2].strip("<>"))
        self.questionData["tag"] = self.getTagAtIndex([0, 1, 3])
        return self.questionData