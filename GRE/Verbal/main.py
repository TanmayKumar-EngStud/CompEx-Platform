import os
import json
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from files.simpleQuestionGeneration import SimpleQuestionGeneration
from files.parentChildQuestionGeneration import ParentChildQuestionGeneration
load_dotenv()

assistant_id_simple_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GRE-Verbal-Simple-Questions"]
assistant_id_parent_child_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GRE-Verbal-Parent-Child-Questions"]

prompt = "<history> - <rc-m> - <4> - <2>"
child_prompts = ["<Main idea> - <4> - <3>", "<Inference> - <4> - <2>", "<Cause> - <5> - <1>"]
llm = None

if ("<rc-" in prompt):
   # parent child question generation
   llm = OpenAIAssistantRunnable(
      model="gpt-4o-mini",
      api_key=os.getenv("OPENAI_API_KEY"),
      assistant_id=assistant_id_parent_child_questions
   )
   parentChildQuestionGeneration = ParentChildQuestionGeneration(llm, prompt)
   
   questionData = parentChildQuestionGeneration.generate_question(child_prompts)
   print(json.dumps(questionData, indent=4))
else:
   # simple question generation
   llm = OpenAIAssistantRunnable(
      model="gpt-4o-mini",
      api_key=os.getenv("OPENAI_API_KEY"),
      assistant_id=assistant_id_simple_questions
   )
   simpleQuestionGeneration = SimpleQuestionGeneration(llm, prompt)
   questionData = simpleQuestionGeneration.generate_question()
   print(json.dumps(questionData, indent=4))



