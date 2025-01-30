from Quants.files.questionComponents import SimpleQuestion
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
import os, json, re
from dotenv import load_dotenv
import random
class SimpleQuestionGeneration:
    def __init__(self, llm=None, prompt=None):
        load_dotenv()
        assistant_id = json.load(open(os.path.join(os.path.dirname(__file__), "../../assistant_ids.json"), "r"))["GRE-Quants-Simple-Questions"]
        if llm is None:
            llm = OpenAIAssistantRunnable(
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
                assistant_id=assistant_id
            )
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}

    def getTagAtIndex(self, indexes):
        tags = []
        for index in indexes:
            tags.extend([x.strip() for x in self.prompt.split(" - ")[index].strip("<>").strip("[]").split(",")])
        return tags

    def generate_question(self):
        questionContent = SimpleQuestion(self.llm, self.prompt)
        self.questionData["thread_id"], self.questionData["question"] = questionContent.generate_questionText()
        self.questionData["title"] = questionContent.generate_questionTitle()
        self.questionData["solution"] = questionContent.generate_questionSolution()
        options, answer = questionContent.generate_questionOptions()
        options_list = list(options.values())
        random.shuffle(options_list)
        self.questionData["options"] = options_list
        self.questionData["answer"] = options[answer]

        pattern = r'<difficulty-level: (\d+)>'
        match = re.search(pattern, self.prompt)
        self.questionData["difficulty"] = int(match.group(1))
        try:
            self.questionData["tag"] = self.getTagAtIndex([0, 1, 3])
        except Exception as e:
            print(f"Error: {self.prompt} the length of the prompt is {len(self.prompt.split('-'))}")
            self.questionData["tag"] = ["Simple"]
        return self.questionData