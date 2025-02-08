import random, json, os, re
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
# GMAT.Integrated_Reasoning.files.
from GMAT.Integrated_Reasoning.files.questionComponents import MSR

class Generate_MSR:
    def __init__(self, prompt):
        load_dotenv()
        assistant_id = json.load(open(os.path.join(os.path.dirname(__file__), "../../assistant_ids.json"), "r"))["Multi-Source-Reasoning"]
        llm = OpenAIAssistantRunnable(
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
                assistant_id=assistant_id
        )
        self.llm = llm
        self.prompt = prompt

        search = re.search(r"total_child_questions: (\d+)", self.prompt)
        self.total_child_questions = 3
        if search:
            self.total_child_questions = int(search.group(1))
        
        self.questionData = {}
        self.MSR = json.load(open(os.path.join(os.path.dirname(__file__), "../combinations/MSR.json")))

    def generate_question(self):
        msr = MSR(self.llm, self.prompt)
        cn = self.MSR["combination_number"]
        sources = {"sources": []}
        # region generating sources
        for source_index in range(1, 4):
            source_type = self.MSR["source_types"][cn%len(self.MSR["source_types"])]
            if cn%len(self.MSR["source_types"]) == 0:
                random.shuffle(self.MSR["source_types"])
            source = {}
            self.questionData["thread_id"], source = msr.generate_SourceInfo(f"Generate SourceInfo_{source_index} having {source_type} of question: {self.prompt}")
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
            focused_skill = self.MSR["focused_skill"][cn%len(self.MSR["focused_skill"])]
            question_style = random.choice(self.MSR["question_style"])
            if cn%len(self.MSR["focused_skill"]) == 0:
                random.shuffle(self.MSR["focused_skill"])
            if cn%len(self.MSR["question_style"]) == 0:
                random.shuffle(self.MSR["question_style"])
            cn +=1
            search = re.search(r"<difficulty_level: (\d+)>", self.prompt)
            # region setting difficulty level
            original_difficulty = int(search.group(1))
            difficulty_level = original_difficulty + random.randint(-1, 1)
            if difficulty_level < 1:
                difficulty_level = 1
            elif difficulty_level > 5:
                difficulty_level = 5
            # endregion
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