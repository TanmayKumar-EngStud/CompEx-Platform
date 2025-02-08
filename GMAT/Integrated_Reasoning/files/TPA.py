# GMAT.Integrated_Reasoning.files.
from GMAT.Integrated_Reasoning.files.questionComponents import TPA
import random
import json
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from dotenv import load_dotenv
import os, re
class Generate_TPA:
    def __init__(self, prompt):
        load_dotenv()
        assistant_id = json.load(open(os.path.join(os.path.dirname(__file__), "../../assistant_ids.json"), "r"))["Two-Part-Analysis"]
        llm = OpenAIAssistantRunnable(
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
                assistant_id=assistant_id
        )
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}

    def generate_question(self):
        difficulty_search = re.search(r"difficulty_level: (\d+)", self.prompt)
        difficulty = 1
        if difficulty_search:
            difficulty = int(difficulty_search.group(1))
        
        tpa = TPA(self.llm, self.prompt)
        
        # Generate question text and components
        thread_id, parentQuestionContent = tpa.generate_ParentQuestionContent()
        self.questionData["type"] = "TPA"
        self.questionData["prompt"] = self.prompt
        self.questionData["thread_id"] = thread_id
        self.questionData["content"] = [parentQuestionContent]
        
        # region preparing difficulty for child Questions
        d1 = difficulty + random.randint(-1, 1)
        d2 = difficulty + random.randint(-1, 1)
        if d1 < 1:
            d1 = 1
        if d2 < 1:
            d2 = 1
        if d1 > 5:
            d1 = 5
        if d2 > 5:
            d2 = 5
        # endregion
        
        # region generating child questions
        questions= tpa.generate_QuestionText([d1, d2])
        q1 = {} 
        q2 = {}
        q1["question"] = questions[0]
        q2["question"] = questions[1]
        
        solutions = tpa.generate_QuestionSolution()
        q1["solution"] = solutions[0]
        q2["solution"] = solutions[1]
        common_options, answers = tpa.generate_QuestionOptions()
        ans1 = common_options[answers["question1"]]
        ans2 = common_options[answers["question2"]]
        q1["answer"] = ans1
        q2["answer"] = ans2

        title = tpa.generate_QuestionTitle()
        self.questionData["title"] = title or "Two Part Analysis Question"
        option_list = list(common_options.values())
        random.shuffle(option_list)
        q1["options"] = option_list
        q2["options"] = option_list
        q1["difficulty"] = d1
        q2["difficulty"] = d2
        q1["tags"] = [self.prompt.split(" - ")[1].strip().strip("<>").strip()]
        q2["tags"] = [self.prompt.split(" - ")[1].strip().strip("<>").strip()]
        # endregion
        self.questionData["questions"] = [q1, q2]
        
        # Set tags and difficulty
        self.questionData["tags"] = ["TPA", self.prompt.split(" - ")[1].strip().strip("<>").strip()]
        self.questionData["difficulty"] = difficulty
            
        return self.questionData

# g = Generate_TPA("<Business> - <Quantitative Skills> - <difficulty_level: 3> - <Bar Chart>")
# res = g.generate_TPA()
# json.dump(res, open("tpa-component.json", "w"))