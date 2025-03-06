# GRE.Quants.files.
from questionComponents import ParentChildQuestion
from google import genai
import os, json, re
from dotenv import load_dotenv
import random
class ParentChildQuestionGeneration:
    def __init__(self, prompt=None, api_IDX = 1):
        load_dotenv()
        api_key = os.getenv(f"API_{api_IDX}")
        self.llm = genai.Client(api_key = api_key)
        with open(os.path.join(os.path.dirname(__file__), "../System_instructions/GRE-Quants-Parent-Child-Questions.txt"), "r") as f:
            self.system_instructions = f.read()
        self.total_child_questions = int(re.search(r"parent_child-(\d+)", prompt).group(1))
        self.prompt = re.sub(r"parent_child-(\d+)", f'total child questions that you would have to generate for this parentChildQuestion will be {self.total_child_questions} so prepare other question data accordigly, prompt: ', prompt)
        self.questionData = {}
        self.thread_id = None
    def generate_question(self):
        self.questionData["type"] = "PS"
        self.questionData["prompt"] = self.prompt
        
        tag = []
        try:
            match = re.search(r"<(.*?)>", self.prompt)
            tag = ["PS"]
            if match:
                first_content = match.group(1)
                tag.append(first_content)
        except Exception as e:
            print(f"Error: {self.prompt} the length of the prompt is {len(self.prompt.split('-'))} exception: {str(e)}")
            tag = ["PS"]
        
        parentChildQuestion = ParentChildQuestion(self.llm, self.system_instructions, self.prompt)
        content = parentChildQuestion.generate_questionGraph()
        self.questionData["content"] = content

        self.questionData["title"] = parentChildQuestion.generate_parentTitle()
        number_of_child_questions = self.total_child_questions
        self.questionData["questions"] = []
        for i in range(number_of_child_questions):
            childQuestionData = {}
            childQuestionData["question"] = parentChildQuestion.generate_childQuestion(i+1)
            childQuestionData["number"] = i+1
            childQuestionData["title"] = parentChildQuestion.generate_childQuestionTitle(i+1)
            childQuestionData["solution"] = parentChildQuestion.generate_childSolution(i+1)
            options, answer = parentChildQuestion.generate_childOptions(i+1)
            childQuestionData["answer"] = options[answer]
            option_list = list(options.values())
            random.shuffle(option_list)
            childQuestionData["options"] = option_list
            childQuestionData["tag"] = tag
            self.questionData["questions"].append(childQuestionData)

        pattern = r'<difficulty-level: (\d+)>'
        match = re.search(pattern, self.prompt)
        self.questionData["difficulty"] = int(match.group(1))
        self.questionData["tag"] = tag

        return self.questionData