import os
import json
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
load_dotenv()


assistant_id = json.load(open(os.path.join(os.path.dirname(__file__), "../../assistant_ids.json"), "r"))["questionText"]


class QuestionText:
    def __init__(self):
        self.llm = OpenAIAssistantRunnable(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            assistant_id=assistant_id
        )

    def generate_question(self, input_data):
        response = self.llm.invoke({"content":input_data})
        return [message.content[0].text.value for message in response][0]

questionText = QuestionText()

print(questionText.generate_question("<[Percentages]> - <2> - <Word Problem>"))
