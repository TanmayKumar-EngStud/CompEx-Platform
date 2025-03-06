import json, re, os
from google.genai import types

def refine_response(response_text):
   """
   A simplified function to handle JSON responses, including those wrapped in ```json code blocks.
   """
   if not response_text:
      return response_text 
   
   try: 
      try:
         json.loads(response_text)
         return response_text
      except json.JSONDecodeError:
         json_block_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
         if json_block_match:
            json_str = json_block_match.group(1).strip()
         else: 
            json_str = response_text
         try:
            json.loads(json_str)
            return json_str
         except json.JSONDecodeError:
# region ✅ 3 levels of json transformation 1️⃣ *,} -> *} ; *,] -> *] 2️⃣ {' -> {" ; [' -> [" ; '} -> "} ; '] -> "] ; '\s*: -> "\s*: 3️⃣ *'\s*, -> *"\s*, ;  ,\s*'* -> ,\s*"* ;
            # *,} -> *} ; *,] -> *]
            json_str = re.sub(r',(\s*})', r'\1', json_str)
            json_str = re.sub(r',(\s*])', r'\1', json_str)
            # {' -> {" ; [' -> [" ; '} -> "} ; '] -> "] ; '\s*: -> "\s*:
            json_str = re.sub(r"(\[\s*)'", r'\1"', json_str)
            json_str = re.sub(r"(\{\s*)'", r'\1"', json_str)
            json_str = re.sub(r"'(\s*\])", r'"\1', json_str)
            json_str = re.sub(r"'(\s*\})", r'"\1', json_str)
            json_str = re.sub(r"'(\s*:)" , r'"\1', json_str)
            try:
               val = json.loads(json_str)
               return json.dumps(val)
            except json.JSONDecodeError:
                # *'\s*, -> *"\s*, ;  ,\s*'* -> ,\s*"* ;
                json_str = re.sub(r"([a-zA-Z0-9\s!.`]\s*)'(\s*,)", r'\1"\2', json_str)
                json_str = re.sub(r"(,\s*)'(\s*[a-zA-Z0-9])", r'\1"\2', json_str)
# endregion
            try:
               val = json.loads(json_str)
               return json.dumps(val)
            except json.JSONDecodeError:
                try:
                    json_str = json_str.replace("\\\"", "'")
                    json_str = json_str.replace("\\", "\\\\")
                    val = json.loads(json_str)
                    return json.dumps(val)
                except json.JSONDecodeError as e:
                    print(f"❌ after trying to remove back slashes: {json_str}.\nError: {str(e)}\n\n")
                    return json_str
               # needs further investigation of such cases.
         except Exception as e:
            print(f"{'#'*13}\nGetting error at internal try block: {str(e)},\n response_text: {response_text}{'#'*23}\n\n")
            return response_text
   except Exception as e:
      print(f"Getting error at first try block: {str(e)}")
      return response_text

class MSR:
   def __init__(self, llm,system_instructions, prompt):
      self.llm = llm
      self.system_instructions = system_instructions
      self.prompt = prompt
      self.messages = []
      self.question_component = []
   
   def ___addMessage(self, component, prompt):
      self.messages.append(prompt)
      self.question_component.append(component)
   
   def ___getResponse(self):
      response = self.llm.models.generate_content(
         model = os.getenv("MODEL"),
         config = types.GenerateContentConfig(
            system_instruction = self.system_instructions
         ),
         contents = self.messages
      )
      print(response.text)
      # here based on the style how we are getting the response, we will make the changes. 
      with open("temp.txt", "w") as f:
         f.write(response)
      return None
   
   def generate_SourceInfo(self, index, source_type, prompt):
      prompt = f"""
      Mode: SourceInfo_{index}
      Source Type: {source_type}
      Prompt: {prompt}
      return: `source_info` and `content`
      """
      self.___addMessage(["source_info", "content"], prompt)

   def generate_MainQuestionTitle(self):
      prompt = f"""
      Mode: QuestionTitle
      return: `title`
      """
      self.___addMessage(["title"], prompt)

   def generate_ChildQuestionText(self, index, prompt):
      prompt = f"""
      Mode: ChildQuestionText_{index}
      Prompt: {prompt}
      return: `question`
      """
      self.___addMessage(["question"], prompt)
   
   def generate_ChildQuestionTitle(self, index):
      prompt = f"""
      Mode: ChildQuestionTitle_{index}
      return: `title`
      """
      self.___addMessage(["title"], prompt)
      
   def generate_ChildQuestionSolution(self, index):
      prompt = f"""
      Mode: ChildQuestionSolution_{index}
      return: `solution`
      """
      self.___addMessage(["solution"], prompt)
   
   def generate_ChildQuestionOptions(self, index):
      prompt = f"""
      Mode: ChildQuestionOptions_{index}
      return: `options`
      """
      self.___addMessage(["options"], prompt)
   
   def get_Response(self):
      self.___getResponse()