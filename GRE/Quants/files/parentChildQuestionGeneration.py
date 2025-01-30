from Quants.files.questionComponents import ParentChildQuestion
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
import os, json, re
from dotenv import load_dotenv
import random
class ParentChildQuestionGeneration:
    def __init__(self, llm=None, prompt=None):
        load_dotenv()
        assistant_id = json.load(open(os.path.join(os.path.dirname(__file__), "../../assistant_ids.json"), "r"))["GRE-Quants-Parent-Child-Questions"]
        if llm is None:
            llm = OpenAIAssistantRunnable(
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
                assistant_id=assistant_id
            )
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}
        self.thread_id = None
    def generate_question(self):
        parentChildQuestion = ParentChildQuestion(self.llm, self.prompt)
        self.thread_id, self.questionData["graph/table"] = parentChildQuestion.generate_questionGraph()

        self.questionData["title"] = parentChildQuestion.generate_parentTitle()
        number_of_child_questions = random.randint(2,4)
        self.questionData["childQuestions"] = []
        for i in range(number_of_child_questions):
            childQuestionData = {}
            childQuestionData["question"] = parentChildQuestion.generate_childQuestion(i)
            childQuestionData["number"] = i
            childQuestionData["title"] = parentChildQuestion.generate_childQuestionTitle(i)
            childQuestionData["solution"] = parentChildQuestion.generate_childSolution(i)
            options, answer = parentChildQuestion.generate_childOptions(i)
            childQuestionData["answer"] = options[answer]
            option_list = list(options.values())
            random.shuffle(option_list)
            childQuestionData["options"] = option_list
            self.questionData["childQuestions"].append(childQuestionData)

        pattern = r'<difficulty-level: (\d+)>'
        match = re.search(pattern, self.prompt)
        self.questionData["difficulty"] = int(match.group(1))
        try:
            self.questionData["tag"] = ["PS", self.prompt.split("-")[3].strip("<>").strip("[]").split(",")]
        except Exception as e:
            print(f"Error: {self.prompt} the length of the prompt is {len(self.prompt.split('-'))}")
            self.questionData["tag"] = ["PS"]
        return self.questionData