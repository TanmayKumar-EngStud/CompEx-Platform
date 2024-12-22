import os
import json
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from files.simpleQuestionGeneration import SimpleQuestionGeneration
from files.dataSufficiencyQuestionGeneration import DataSufficiencyQuestionGeneration
load_dotenv()

assistant_id_simple_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GRE-Quants-Simple-Questions"]
assistant_id_parent_child_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GRE-Quants-Parent-Child-Questions"]
assistant_id_data_sufficiency_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GRE-Quants-Data-Sufficiency-Questions"]
prompt = "<[Percentages]> - <1> - <straight forward> - < Data Sufficiency>"
llm = None
if ("data sufficiency" in prompt.lower()):
   llm = OpenAIAssistantRunnable(
      model="gpt-4o-mini",
      api_key=os.getenv("OPENAI_API_KEY"),
      assistant_id=assistant_id_data_sufficiency_questions
   )
   data_sufficiency_question_generation = DataSufficiencyQuestionGeneration(llm, prompt)
   questionData = data_sufficiency_question_generation.generate_question()
   print(json.dumps(questionData, indent=4))

elif ("graph" in prompt.lower() or "table" in prompt.lower()):
   llm = OpenAIAssistantRunnable(
      model="gpt-4o-mini",
      api_key=os.getenv("OPENAI_API_KEY"),
      assistant_id=assistant_id_parent_child_questions
   )
else:
   # Simple Question Generation
   llm = OpenAIAssistantRunnable(
      model="gpt-4o-mini",
      api_key=os.getenv("OPENAI_API_KEY"),
      assistant_id=assistant_id_simple_questions
   )
   simpleQuestionGeneration = SimpleQuestionGeneration(llm, prompt)
   questionData = simpleQuestionGeneration.generate_question()
   print(json.dumps(questionData, indent=4))