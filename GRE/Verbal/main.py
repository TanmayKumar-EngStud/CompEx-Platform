import os
import json
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from files.simpleQuestionGeneration import SimpleQuestionGeneration

load_dotenv()

assistant_id_simple_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GRE-Verbal-Simple-Questions"]
assistant_id_parent_child_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GRE-Verbal-Parent-Child-Questions"]

prompt = "<history> - <tc-1> - <1> - <1>"

llm = None

# simple question generation
llm = OpenAIAssistantRunnable(
   model="gpt-4o-mini",
   api_key=os.getenv("OPENAI_API_KEY"),
   assistant_id=assistant_id_simple_questions
)

simpleQuestionGeneration = SimpleQuestionGeneration(llm, prompt)
questionData = simpleQuestionGeneration.generate_question()
print(json.dumps(questionData, indent=4))

# parent child question generation
