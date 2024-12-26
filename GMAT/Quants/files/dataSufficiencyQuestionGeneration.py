from files.questionComponents import DataSufficiencyQuestion

class DataSufficiencyQuestionGeneration:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}
        self.thread_id = None
    def generate_question(self):
        questionContent = DataSufficiencyQuestion(self.llm, self.prompt)
        if("graph" in self.prompt.lower() or "table" in self.prompt.lower()):
            self.thread_id, self.questionData["graph/table"] = questionContent.generate_questionGraph()
        self.questionData["thread_id"], self.questionData["question"], self.questionData["statements"] = questionContent.generate_questionText()
        self.questionData["title"] = questionContent.generate_questionTitle()
        self.questionData["solution"], self.questionData["answer"] = questionContent.generate_questionSolution()
        self.questionData["options"] = ["Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient", "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient", "BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient", "EITHER statement ALONE is sufficient", "Statements (1) and (2) TOGETHER are NOT sufficient"]
        self.questionData["answer"] = self.questionData["options"][ord(self.questionData["answer"]) - ord("A")]
        return self.questionData