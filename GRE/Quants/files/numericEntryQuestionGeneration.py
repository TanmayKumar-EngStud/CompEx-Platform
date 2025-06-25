import json, re, os
from dotenv import load_dotenv
from google import genai

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.components.question_components import create_question_component
from core.components.adapters.gre_adapter import GREAdapter
class NumericEntryQuestionGeneration:
   def __init__(self, global_state, lock, api_IDX, prompt):
      load_dotenv()
      self.global_state = global_state
      self.lock = lock
      api_key = os.getenv(f"API_{api_IDX}")
      self.llm = genai.Client(api_key = api_key)
      with open(os.path.join(os.path.dirname(__file__), "../System_instructions/GRE-Quants-Numeric-Entry.txt"), "r") as f:
         self.system_instructions = f.read()
      self.prompt = prompt
      self.questionData = {}

      self.thread_id = None
   
   def generate_question(self):
      self.questionData["type"] = "NE"
      self.questionData["prompt"] = self.prompt
      if "graph" in self.prompt.lower() or "table" in self.prompt.lower():
         # Create parent-child component for graph/table content
         pc_component = create_question_component(
            question_type=QuestionType.READING_COMPREHENSION,
            llm=self.llm,
            system_instructions=self.system_instructions,
            global_state=self.global_state,
            lock=self.lock,
            prompt=self.prompt,
            exam_type=ExamType.GRE
         )
         numericEntryQuestion = GREAdapter.adapt_parent_child_question(pc_component)
         content = numericEntryQuestion.generate_questionGraph()
         self.questionData["content"] = content
      
      # Create simple question component for numeric entry
      simple_component = create_question_component(
         question_type=QuestionType.NUMERIC_ENTRY,
         llm=self.llm,
         system_instructions=self.system_instructions,
         global_state=self.global_state,
         lock=self.lock,
         prompt=self.prompt,
         exam_type=ExamType.GRE
      )
      numericEntryQuestion = GREAdapter.adapt_simple_question(simple_component)
      self.questionData["question"] = numericEntryQuestion.generate_questionText()
      self.questionData["title"] = numericEntryQuestion.generate_questionTitle()
      self.questionData["solution"], self.questionData["answer"] = numericEntryQuestion.generate_questionSolution(isNE = True)

      try:
            match = re.search(r"<(.*?)>", self.prompt)
            tag = ["Numeric Entry"]
            if match:
                first_content = match.group(1)
                tag.append(first_content)
            self.questionData["tag"] = tag
      except Exception as e:
            print(f"Error: {self.prompt} the length of the prompt is {len(self.prompt.split('-'))}")
            self.questionData["tag"] = ["Numeric Entry"]

      pattern = r'<difficulty-level: (\d+)>'
      match = re.search(pattern, self.prompt)
      self.questionData["difficulty"] = int(match.group(1))

      return self.questionData