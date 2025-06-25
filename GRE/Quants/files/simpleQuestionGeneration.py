import os, json, re, random
from google import genai
from dotenv import load_dotenv

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.components.question_components import create_question_component
from core.components.adapters.gre_adapter import GREAdapter
class SimpleQuestionGeneration:
    def __init__(self, global_state, lock, api_IDX, prompt):
        load_dotenv()
        self.global_state = global_state
        self.lock = lock
        api_key = os.getenv(f"API_{api_IDX}")
        self.llm = genai.Client(api_key = api_key)
        self.prompt = prompt
        self.questionData = {}
        with open(os.path.join(os.path.dirname(__file__), "../System_instructions/GRE-Quants-Simple-Questions.txt"), "r") as f:
            self.system_instructions = f.read()

    def getTagAtIndex(self, indexes):
        tags = []
        for index in indexes:
            tags.extend([x.strip() for x in self.prompt.split(" - ")[index].strip("<>").strip("[]").split(",")])
        return tags

    def generate_question(self):
        if "(multi-correct MCQ)" in self.prompt:
            self.questionData["type"] = "MCQ-Multi"
        else:
            self.questionData["type"] = "MCQ-Single"
        self.questionData["prompt"] = self.prompt
        # Create unified component and wrap with GRE adapter
        component = create_question_component(
            question_type=QuestionType.PROBLEM_SOLVING,
            llm=self.llm,
            system_instructions=self.system_instructions,
            global_state=self.global_state,
            lock=self.lock,
            prompt=self.prompt,
            exam_type=ExamType.GRE
        )
        questionContent = GREAdapter.adapt_simple_question(component)
        self.questionData["question"] = questionContent.generate_questionText()
        self.questionData["title"] = questionContent.generate_questionTitle()
        self.questionData["solution"] = questionContent.generate_questionSolution()
        options, answer = questionContent.generate_questionOptions()
        options_list = list(options.values())
        
        if isinstance(answer, list):
            ans = []
            for i in answer:
                ans.append(options[i])
            self.questionData["answer"] = ans
        else:
            self.questionData["answer"] = options[answer]
        random.shuffle(options_list)
        self.questionData["options"] = options_list

        pattern = r'<difficulty-level: (\d+)>'
        match = re.search(pattern, self.prompt)
        self.questionData["difficulty"] = int(match.group(1))
        try:
            match = re.search(r"<(.*?)>", self.prompt)
            if "(multi-correct MCQ)" in self.prompt:
                tag = ["MCQ-Multi correct"]
            else:
                tag = ["MCQ-Single correct"]
            if match:
                first_content = match.group(1)
                tag.append(first_content)
            self.questionData["tag"] = tag
        except Exception as e:
            print(f"Error: {self.prompt} the length of the prompt is {len(self.prompt.split('-'))} exception: {str(e)}")
            self.questionData["tag"] = ["MCQ"]

        return self.questionData