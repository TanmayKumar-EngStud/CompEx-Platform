import json, re

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

            # *'\s*, -> *"\s*, ;  ,\s*'* -> ,\s*"* ;
            json_str = re.sub(r"([a-zA-Z0-9\s!.`]\s*)'(\s*,)", r'\1"\2', json_str)
            json_str = re.sub(r"(,\s*)'(\s*[a-zA-Z0-9])", r'\1"\2', json_str)
# endregion
            try:
               json.loads(json_str)
               return json_str
            except json.JSONDecodeError:
               print(f"this is how json_string looks like after level 3 replacements: {json_str}")
               # needs further investigation of such cases.
         except Exception as e:
            print(f"{'#'*13}\nGetting error at internal try block: {str(e)},\n response_text: {response_text}{'#'*23}\n\n")
            return response_text
   except Exception as e:
      print(f"Getting error at first try block: {str(e)}")
      return response_text

class ParentChildQuestion:
    def __init__(self, llm, prompt, number_of_child_questions, thread_id=None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id
        self.number_of_child_questions = number_of_child_questions
        self.number_of_passages = number_of_child_questions
    def generate_parentPassage(self):
        passages = []
        for i in range(self.number_of_passages):
            if self.thread_id:
                response = self.llm.invoke({"content":f"Passage {i+1} of {self.number_of_passages}: {self.prompt}", "thread_id": self.thread_id})
            else:
                response = self.llm.invoke({"content":f"Passage {i+1} of {self.number_of_passages}: {self.prompt}"})
                self.thread_id = response[0].thread_id
            try:
                message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
                passages.append(message["passage"])
            except Exception as e:
                raise Exception(f"GMAT Verbal, Error: message received for parentPassage is: \n{response[0].content[0].text.value}\nerror: {str(e)}\n")
        return self.thread_id, passages
    
    def generate_parentTitle(self):
        response = self.llm.invoke({"content": f"ParentTitle", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            raise Exception(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_parentTitle) is: \n{response[0].content[0].text.value}\nerror: {str(e)}\n")
    def generate_childQuestionTitle(self, index):
        response = self.llm.invoke({"content": f"ChildQuestionTitle: {index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            raise Exception(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_childQuestionTitle) is: \n{response[0].content[0].text.value}\nerror: {str(e)}\n")
    def generate_childQuestion(self, index, child_prompt=""):
        response = self.llm.invoke({"content": f"ChildQuestion: {index} of {child_prompt}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["question"]
        except Exception as e:
            raise Exception(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_childQuestion) is: \n{response[0].content[0].text.value}\n\n")
            
    def generate_childOptions(self, index):
        response = self.llm.invoke({"content": f"ChildOptions: {index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["options"], message["answer"]
        except Exception as e:
            raise Exception(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_childOptions) is: \n{response[0].content[0].text.value}\nerror: {str(e)}\n")
    def generate_childSolution(self, index):
        response = self.llm.invoke({"content": f"ChildSolution: {index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["solution"]
        except Exception as e:
            raise Exception(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_childSolution) is: \n{response[0].content[0].text.value}\nerror: {str(e)}\n")

class SimpleQuestion:
    def __init__(self, llm, prompt, thread_id= None):
        self.llm = llm
        self.thread_id = thread_id
        self.prompt = prompt
    def generate_QuestionPassage(self):
        passages = []

        for i in range(2):
            try:
                if self.thread_id:
                    response = self.llm.invoke({"content": f"Passage {i+1} of 2: {self.prompt}", "thread_id": self.thread_id})
                else:
                    response = self.llm.invoke({"content": f"Passage {i+1} of 2: {self.prompt}"})
                    self.thread_id = response[0].thread_id
            except Exception as e:
                print(f"Error in LLM invoke for passage {i+1}: {str(e)}")
                return "", []
            try:
                message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
                if "passage" not in message:
                    raise KeyError(f"No 'passage' key in response for passage {i+1}")
                passages.append(message["passage"])
            except Exception as e:
                error_msg = f"GMAT Verbal, Error: Failed to process passage {i+1}\n"
                error_msg += f"Response: {response[0].content[0].text.value if response else 'No response'}\n"
                error_msg += f"Error: {str(e)}"
                raise Exception(error_msg)
        
        if not passages:
            raise Exception("No passages were generated")
            
        return self.thread_id, passages
    
    def generate_questionText(self):
        if self.thread_id:
            response = self.llm.invoke({"content":f"QuestionText: {self.prompt}", "thread_id": self.thread_id})
        else:
            response = self.llm.invoke({"content":f"QuestionText: {self.prompt}"})
            self.thread_id = response[0].thread_id
        try:
            response_text = refine_response([message.content[0].text.value for message in response][0])
            message = json.loads(response_text)
            return message["question"]
        except Exception as e:
            raise Exception(f"GMAT Verbal, Error: message received for simpleQuestion(generate_questionText) is: \n{[message.content[0].text.value for message in response][0]}\nerror: {str(e)}\n")
    
    def generate_questionTitle(self):
        response = self.llm.invoke({"content":f"QuestionTitle", "thread_id": self.thread_id})
        try:
            response_text = refine_response([message.content[0].text.value for message in response][0])
            message = json.loads(response_text)
            return message["title"]
        except Exception as e:
            raise Exception(f"GMAT Verbal, Error: message received for simpleQuestion(generate_questionTitle) is: \n{[message.content[0].text.value for message in response][0]}\nerror: {str(e)}\n")
    def generate_questionSolution(self):
        response = self.llm.invoke({"content":f"QuestionSolution", "thread_id": self.thread_id})
        try:
            response_text = refine_response([message.content[0].text.value for message in response][0])
            if isinstance(response_text, dict):
                message = response_text
            else:
                message = json.loads(response_text)    
            return message["solution"]
        except Exception as e:
            raise Exception(f"GMAT Verbal, Error: message received for simpleQuestion(generate_questionSolution) is: \n{response[0].content[0].text.value}\nerror: {str(e)}\n")
    def generate_questionOptions(self):
      response = self.llm.invoke({"content":f"QuestionOptions", "thread_id": self.thread_id})
      try:
         raw_response = response[0].content[0].text.value
         json_string = refine_response(raw_response)
         message = json.loads(json_string)
         return message["options"], message["answer"]
      except Exception as e:
         raise Exception(f"GMAT Verbal, Error: message received for simpleQuestion(generate_questionOptions) is: \n{response[0].content[0].text.value}\n\nrefined_response: {json_string}\nerror: {str(e)}\n")

