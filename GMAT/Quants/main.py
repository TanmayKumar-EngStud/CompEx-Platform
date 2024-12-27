import os
import json
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from files.simpleQuestionGeneration import SimpleQuestionGeneration
from files.parentChildQuestionGeneration import ParentChildQuestionGeneration
from files.dataSufficiencyQuestionGeneration import DataSufficiencyQuestionGeneration
load_dotenv()

assistant_id_simple_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Quants-Simple-Questions"]
assistant_id_data_sufficiency_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Quants-Data-Sufficiency-Questions"]
assistant_id_parent_child_questions = json.load(open(os.path.join(os.path.dirname(__file__), "../assistant_ids.json"), "r"))["GMAT-Quants-Parent-Child-Questions"]

prompt = "<Algebra> - <1> - <word problem> - <problem solving> - <bar graph>"

if ("data sufficiency" in prompt.lower()):
   llm = OpenAIAssistantRunnable(
      model="gpt-4o-mini",
      api_key=os.getenv("OPENAI_API_KEY"),
      assistant_id=assistant_id_data_sufficiency_questions
   )
   dataSufficiencyQuestionGeneration = DataSufficiencyQuestionGeneration(llm, prompt)
   
   questionData = dataSufficiencyQuestionGeneration.generate_question()
   print("Data Sufficiency Question Generation")
   print(json.dumps(questionData, indent=4))
elif ("graph" in prompt.lower()):
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