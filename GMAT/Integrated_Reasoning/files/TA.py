# `<TA> - <focused_skill> - <TableType> - <QuestionType> - <QuestionTheme> - <DifficultyLevel>`

import random
# GMAT.Integrated_Reasoning.files.
from questionComponents import TA
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from dotenv import load_dotenv
import os, re, json
class Generate_TA:
    def __init__(self, prompt):
        load_dotenv()
        assistant_id = json.load(open(os.path.join(os.path.dirname(__file__), "../../assistant_ids.json"), "r"))["Table-Analysis"]
        llm = OpenAIAssistantRunnable(
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
                assistant_id=assistant_id
        )
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}
    def generate_TA(self):
        ta = TA(self.llm, self.prompt)
        difficulty_search = re.search(r"difficulty_level: (\d+)", self.prompt)
        difficulty = 1
        if difficulty_search:
            difficulty = int(difficulty_search.group(1))
        no_rows = difficulty + random.randint(5, 7)
        no_cols = difficulty + random.randint(3, 5)
        self.questionData["thread_id"], self.questionData["tables"] = ta.generate_QuestionTable(no_rows, no_cols)
        self.questionData["question"] = ta.generate_QuestionText()
        self.questionData["title"] = ta.generate_QuestionTitle()
        options, answers = ta.generate_QuestionOptions()
        self.questionData["solution"] = ta.generate_QuestionSolution()
        option_list = list(options.values())
        random.shuffle(option_list)
        self.questionData["options"] = option_list
        self.questionData["answer"]= {options[key]: answers[key] for key in options}
        self.questionData["tags"] = ["TA", self.prompt.split(" - ")[2].strip().strip('<>').strip(), self.prompt.split(" - ")[3].strip().strip('<>').strip(), self.prompt.split(" - ")[1].strip().strip('<>').strip()]
        self.questionData["difficulty"] = difficulty
        return self.questionData

g = Generate_TA("<TA> - <Quantitative Skills> - <Time-SeriesTable> - <Inferred/Conflicting type> - <Sales> - <difficulty_level: 3>")
res = g.generate_TA()
json.dump(res, open("ta-component.json", "w"))