import os
import json
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from files.simpleQuestionGeneration import SimpleQuestionGeneration
from files.parentChildQuestionGeneration import ParentChildQuestionGeneration

load_dotenv()

assistant_id_simple_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Verbal-Simple-Questions"]
assistant_id_parent_child_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Verbal-Parent-Child-Questions"]

prompt = "<Science and Technology> - <rc-s> - <1> - <1>"

if("rc" in prompt.lower()):
   llm = OpenAIAssistantRunnable(
      model="gpt-4o-mini",
      api_key=os.getenv("OPENAI_API_KEY"),
      assistant_id=assistant_id_parent_child_questions
   )
   parentChildQuestionGeneration = ParentChildQuestionGeneration(llm, prompt)
   questionData = parentChildQuestionGeneration.generate_question()
   print("Parent Child Question Generation")
   print(json.dumps(questionData, indent=4))
else:
   llm = OpenAIAssistantRunnable(
      model="gpt-4o-mini",
      api_key=os.getenv("OPENAI_API_KEY"),
      assistant_id=assistant_id_simple_questions
   )
   simpleQuestionGeneration = SimpleQuestionGeneration(llm, prompt)
   questionData = simpleQuestionGeneration.generate_question()
   print("Simple Question Generation")
   print(json.dumps(questionData, indent=4))
   