import random, json, os, re
from dotenv import load_dotenv
from google import genai
# GMAT.Integrated_Reasoning.files.
# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter

class Generate_MSR:
    def __init__(self, global_state, lock, api_IDX, prompt):
        load_dotenv()
        self.global_state = global_state
        self.lock = lock
        api_key = os.getenv(f"API_{api_IDX}")

        client = genai.Client(api_key=api_key)
        self.llm = client
        self.prompt = prompt
        with open(os.path.join(os.path.dirname(__file__), "../System_instructions/Multi-Source-Reasoning.txt"), "r") as f:
            self.system_instructions = f.read()
        search = re.search(r"total_child_questions: (\d+)", self.prompt)
        self.total_child_questions = 3
        if search:
            self.total_child_questions = int(search.group(1))
        
        self.questionData = {}
        self.MSR = json.load(open(os.path.join(os.path.dirname(__file__), "../combinations/MSR.json")))

    def generate_question(self): 
        # Create unified component and wrap with GMAT adapter
        component = create_question_component(
            question_type=QuestionType.MULTI_SOURCE_REASONING,
            llm=self.llm,
            system_instructions=self.system_instructions,
            global_state=self.global_state,
            lock=self.lock,
            prompt=self.prompt,
            exam_type=ExamType.GMAT
        )
        msr = GMATAdapter.adapt_multi_source_reasoning(component)
        cn = self.MSR["combination_number"]
        sources = {"sources": []}
        # region generating sources
        for source_index in range(1, 4):
            source_type = random.choice(self.MSR["source_types"])
            source = {}
            source = msr.generate_SourceInfo(f"Generate SourceInfo_{source_index} having {source_type} of question: {self.prompt}")
            sources["sources"].append(source)
            cn +=1
        self.questionData["type"] = "MSR"
        self.questionData["prompt"] = self.prompt

        self.questionData["content"] = sources
        # endregion
        self.questionData["title"] = msr.generate_MainQuestionTitle()
        self.questionData["questions"] = []
        cn = self.MSR["combination_number"]
        collective_tags = set()
        # region generating questions
        for source_index in range(1, self.total_child_questions+1):
            question = {}
            focused_skill = random.choice(self.MSR["focused_skill"])
            question_style = random.choice(self.MSR["question_style"])
            search = re.search(r"<difficulty_level: (\d+)>", self.prompt)
            # region setting difficulty level
            original_difficulty = int(search.group(1))
            difficulty_level = original_difficulty + random.randint(-1, 1)
            if difficulty_level < 1:
                difficulty_level = 1
            elif difficulty_level > 5:
                difficulty_level = 5
            # endregion
            question["type"] = question_style
            question["prompt"] = f"ChildQuestion: {source_index} <{focused_skill}> - <{question_style}> - <{difficulty_level}>"
            question["question"] = msr.generate_QuestionText(question["prompt"])
            question["title"] = msr.generate_QuestionTitle(f"ChildQuestionTitle: {source_index}")
            question["solution"] = msr.generate_QuestionSolution(f"ChildQuestionSolution: {source_index}")
            options = []
            self.questionData["type"] += f" - {question_style}"
            if question_style == "MCQ (5 options MCQ)":
                options, correct_option = msr.generate_QuestionOptions(f"ChildQuestionOptions: {source_index}", question_style)
                question["answer"] = options[correct_option]
                options = list(options.values())
            else:
                question["answer"] = msr.generate_QuestionOptions(f"ChildQuestionOptions: {source_index}", question_style)
                options = list(question["answer"].values())
            question_style = re.sub(r' \(.*?\)', '', question_style)

            random.shuffle(options)
            option_list = list(options)
            random.shuffle(option_list)
            question["options"] = option_list
            question["tags"] = [focused_skill, question_style, "MSR", source_type]
            collective_tags.update(question["tags"])
            question["difficulty"] = difficulty_level
            self.questionData["questions"].append(question)

        self.questionData["title"] = msr.generate_MainQuestionTitle()
        self.questionData["tags"] = list(collective_tags)
        search = re.search(r"<difficulty_level: (\d+)>", self.prompt)
        self.questionData["difficulty"] = int(search.group(1))
        json.dump(self.MSR, open(os.path.join(os.path.dirname(__file__), "../combinations/MSR.json"), "w"))
        return self.questionData


# g = Generate_MSR("<MSR> - <total_child_questions: 3> - <Business> - <difficulty_level: 4>")
# content = g.generate_MSR()
# json.dump(content, open(os.path.join(os.path.dirname(__file__), "MSR-component.json"), "w"))