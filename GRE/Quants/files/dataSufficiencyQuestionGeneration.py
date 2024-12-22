from files.questionComponents import QuestionText, QuestionTitle, QuestionSolution, QuestionGraph 

class DataSufficiencyQuestionGeneration:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}
        self.thread_id = None
    def generate_question(self):
        if("graph" in self.prompt.lower()):
            questionGraph = QuestionGraph(self.llm, self.prompt)
            self.thread_id, self.questionData["graph"] = questionGraph.generate_questionGraph()
        else:
            self.thread_id = None
            self.questionData["graph"] = None
        if(self.thread_id is not None):
            questionText = QuestionText(self.llm, self.thread_id)
            self.questionData["thread_id"], self.questionData["question"] = questionText.generate_questionText(self.prompt)

        questionTitle = QuestionTitle(self.llm, self.questionData["thread_id"])
        self.questionData["title"] = questionTitle.generate_questionTitle()

        questionSolution = QuestionSolution(self.llm, self.questionData["thread_id"])
        self.questionData["solution"], self.questionData["answer"] = questionSolution.generate_questionSolution()
        self.questionData["options"] = ["Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient", "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient", "BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient", "EITHER statement ALONE is sufficient", "Statements (1) and (2) TOGETHER are NOT sufficient"]
        self.questionData["answer"] = self.questionData["options"][ord(self.questionData["answer"]) - ord("A")]
        return self.questionData