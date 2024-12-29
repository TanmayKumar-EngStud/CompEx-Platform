import os
import json
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable
from files.GI import Generate_GI
from files.MSR import Generate_MSR

load_dotenv()

assistant_id_graphic_interpretation = json.load(open(os.path.join(os.path.dirname(__file__), '../assistant_ids.json'), 'r'))['Graphic-Interpretation']
assistant_id_multi_source_reasoning = json.load(open(os.path.join(os.path.dirname(__file__), '../assistant_ids.json'), 'r'))['Multi-Source-Reasoning']
assistant_id_table_analysis = json.load(open(os.path.join(os.path.dirname(__file__), '../assistant_ids.json'), 'r'))['Table-Analysis']
assistant_id_two_part_analysis = json.load(open(os.path.join(os.path.dirname(__file__), '../assistant_ids.json'), 'r'))['Two-Part-Analysis']

## Prompts example
#prompt = "<Graphic Interpretation> - <bar chart> - <Sales> - <1>"
prompt = "<Multi Source Reasoning> - <table> - <Sales> - <1>"

if("graphic interpretation" in prompt.lower()):
   llm = OpenAIAssistantRunnable(
      model="gpt-4o-mini",
      api_key=os.getenv("OPENAI_API_KEY"),
      assistant_id=assistant_id_graphic_interpretation
   )
   gi = Generate_GI(llm, prompt)
   gi_question = gi.generate_GI()
   print(json.dumps(gi_question, indent=4))

elif("multi source reasoning" in prompt.lower()):
   llm = OpenAIAssistantRunnable(
      model="gpt-4o-mini",
      api_key=os.getenv("OPENAI_API_KEY"),
      assistant_id=assistant_id_multi_source_reasoning
   )
   msr = Generate_MSR(llm, prompt)
   msr_question = msr.generate_MSR()
   print(json.dumps(msr_question, indent=4))
