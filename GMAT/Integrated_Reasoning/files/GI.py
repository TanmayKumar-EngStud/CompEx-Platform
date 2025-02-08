import random, json, os,re
# GMAT.Integrated_Reasoning.files.
from GMAT.Integrated_Reasoning.files.questionComponents import GI 
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from dotenv import load_dotenv
class Generate_GI:
    def __init__(self, prompt):
        load_dotenv()
        assistant_id = json.load(open(os.path.join(os.path.dirname(__file__), "../../assistant_ids.json"), "r"))["Graphic-Interpretation"]
        llm = OpenAIAssistantRunnable(
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
                assistant_id=assistant_id
        )
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}
    def generate_question(self):
        gi = GI(self.llm, self.prompt)
        self.questionData["type"] = "GI"
        self.questionData["prompt"] = self.prompt
        self.questionData["thread_id"], self.questionData["content"] = gi.generate_questionGraph()
        self.questionData["question"] = gi.generate_questionText()
        self.questionData["title"] = gi.generate_questionTitle()
        self.questionData["solution"] = gi.generate_questionSolution()
        options, correct_option = gi.generate_questionOptions()

        answer_list = []
        for i in range(len(options)):
            answer_list.append(options[i][correct_option[i]])

        shuffled_options = []
        for option_dict in options:
            # Convert dictionary values to a list
            value_list = list(option_dict.values())
            # Shuffle the list
            random.shuffle(value_list)
            # Append the shuffled list to the result
            shuffled_options.append(value_list)
        self.questionData["options"] = shuffled_options
        self.questionData["answer"] = answer_list

        # print(f"options: \n{shuffled_options}\n\n answer: {answer_list}\n\n")
        self.questionData["tags"] = ["GI", self.prompt.split("-")[2].strip().strip('<>').strip()]
        difficulty = re.search(r"<difficulty_level: (\d+)>", self.prompt)
        self.questionData["difficulty"] = int(difficulty.group(1))
        return self.questionData
    
# g = Generate_GI("<GI> - <Bar Chart> - <difficulty_level: 4>")
# content = g.generate_GI()
# json.dump(content, open(os.path.join(os.path.dirname(__file__), "GI-component.json"), "w"))