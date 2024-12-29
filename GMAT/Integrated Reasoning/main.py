import os
import json
from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable

load_dotenv()

assistant_id_graphic_interpretation = json.load(open(os.path.join(os.path.dirname(__file__), '../assistant_ids.json'), 'r'))['Graphic-Interpretation']
assistant_id_multi_source_reasoning = json.load(open(os.path.join(os.path.dirname(__file__), '../assistant_ids.json'), 'r'))['Multi-Source-Reasoning']
assistant_id_table_analysis = json.load(open(os.path.join(os.path.dirname(__file__), '../assistant_ids.json'), 'r'))['Table-Analysis']
assistant_id_two_part_analysis = json.load(open(os.path.join(os.path.dirname(__file__), '../assistant_ids.json'), 'r'))['Two-Part-Analysis']

prompt = "<Graphic Interpretation> - <bar chart> - <Sales> - <1>"

if("graphic interpretation" in prompt.lower()):
   llm = OpenAIAssistantRunnable(
      model="gpt-4o-mini",
      api_key=os.getenv("OPENAI_API_KEY"),
      assistant_id=assistant_id_graphic_interpretation
   )

