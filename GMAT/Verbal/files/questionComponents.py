import json, re

warning = "\nWARNING: please retry this, your output should strictly follow json format so that python program can capture question component properly, use (`) symbol instead of single quote and every key and value should be enclosed in double quotes"

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

max_retries = 3
class ParentChildQuestion:
    def __init__(self, llm, prompt, number_of_child_questions, thread_id=None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id
        self.number_of_child_questions = number_of_child_questions
        self.number_of_passages = number_of_child_questions
    
    def ___getResponse(self, prompt, warn= False):
        prompt += (f", {warning}" if warn else "")
        try: 
            if self.thread_id:
                response = self.llm.invoke({"content": prompt, "thread_id": self.thread_id})
            else:
                response = self.llm.invoke({"content": prompt})
                self.thread_id = response[0].thread_id
            val = [message.content[0].text.value for message in response][0]
            return val
        except Exception as e:
            print(f"{prompt}")
            print(f"failed in generating response by self.llm.invoke: {response}")
            print(f"{str(e)}")
            return None
    
    def _retry_generate(self, func, *args):
        last_error = None
        for attempt in range(max_retries):
            try:
                result = func(*args, warn = True if attempt else False)
                if result:
                    return result
                print(f"Retrying {func.__name__} - attempt {attempt +1}/ {max_retries}")
            except Exception as e:
                last_error = str(e)
                print(f"Error in attempt {attempt +1}: {last_error}")
        if last_error:
            print(f"All attempts failed. Last error: {last_error}")

    def generate_parentPassage(self):
        def _generate(warn= False):
            passages = []
            for i in range(self.number_of_passages):
                prompt = f"Passage {i+1} of {self.number_of_passages}: {self.prompt}"
                response= self.___getResponse(prompt, warn)
                try: 
                    message = json.loads(refine_response(response))
                    passages.append(message["passage"])
                except Exception as e:
                    print(f"GMAT Verbal, error: message received for parentPassage is: \n{response} and \nerror: {str(e)}")
                    return None
            return passages
        result_passages = self._retry_generate(_generate)
        return self.thread_id, result_passages
    
    def generate_parentTitle(self):
        def _generate(warn= False):
            prompt = "ParentTitle"
            response = self.___getResponse(prompt, warn)
            try: 
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(f"GMAT Verbal, error: message received for parentTitle is: \n{response} and \nerror: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_childQuestionTitle(self, index):
        def _generate(warn = False):
            prompt = f"ChildQuestionTitle: {index}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_childQuestionTitle) is:\n {response}\n\n{str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_childQuestion(self, index, child_prompt=""):
        def _generate(warn= False):
            prompt = f"ChildQuestion: {index} of {child_prompt}"
            response = self.___getResponse(prompt, warn)
            try: 
                message = json.loads(refine_response(response))
                return message["question"]
            except Exception as e:
                print(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_childQuestion) is: \n{response}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_childOptions(self, index):
        def _generate(warn= False):
            prompt = f"ChildOptions: {index}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["options"], message["answer"]
            except Exception as e:
                print(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_childOptions) is: \n{response}\n Error: {str(e)}")
                return None
        result_options, result_answer = self._retry_generate(_generate)
        return result_options, result_answer

    def generate_childSolution(self, index):
        def _generate(warn= False):
            prompt = f"ChildSolution: {index}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["solution"]
            except Exception as e:
                print(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_childSolution) is: \n{response}\n Error: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result
class SimpleQuestion:
    def __init__(self, llm, prompt, thread_id= None):
        self.llm = llm
        self.thread_id = thread_id
        self.prompt = prompt
    
    def ___getResponse(self,prompt, warn = False):
      prompt += (f", {warning}" if warn else "")
      try:
         if self.thread_id:
            response = self.llm.invoke({"content": prompt, "thread_id": self.thread_id})
         else:
            response = self.llm.invoke({"content": prompt})
            self.thread_id = response[0].thread_id
         val = [message.content[0].text.value for message in response][0]
         return val
      except Exception as e:
         print(f"{prompt}")
         print(f"failed in generating response by self.llm.invoke: {response}")
         print(f"{str(e)}")
         return None

    def _retry_generate(self, func, *args):
      last_error = None
      for attempt in range(max_retries):
         try: 
            result = func(*args, warn = True if attempt else False)
            if result:
               return result
            print(f"Retrying {func.__name__} - attempt {attempt + 1}/ {max_retries}")
         except Exception as e:
            last_error = str(e)
            print(f"Error in attempt {attempt + 1}: {last_error}")
      
      if last_error:
         print(f"All attempts failed. Last error: {last_error}")
         return None
      
    def generate_QuestionPassage(self):
        def _generate(warn= False):
            passages =[]
            for i in range(2):
                prompt = f"Passage {i+1} of 2: {self.prompt}"
                response = self.___getResponse(prompt, warn)
                try:
                    message = json.loads(refine_response(response))
                    passages.append(message["passage"])
                except Exception as e:
                    passage = []
                    error_msg = f"GMAT Verbal, Error: Failed to process passage {i+1}\n"
                    error_msg += f"Response: {response[0].content[0].text.value if response else 'No response'}\n"
                    error_msg += f"Error: {str(e)}"
                    print(error_msg)
                    return None
            return passages
        result = self._retry_generate(_generate)
        return self.thread_id, result

    
    def generate_questionText(self):
        def _generate(warn= False):
            prompt = f"QuestionText: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["question"]
            except Exception as e:
                print(f"GMAT Verbal, Error message received for simpleQuestion(generate_question) is: \n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionTitle(self):
        def _generate(warn= False):
            prompt = f"QuestionTitle"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(f"GMAT Verbal, Error: message received for simpleQuestion(generate_questionTitle) is: \n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionSolution(self):
        def _generate(warn = False):
            prompt = f"QuestionSolution"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["solution"]
            except Exception as e:
                print(f"GMAT Verbal, Error: message received for simpleQuestion(generate_questionSolution): {response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionOptions(self):
      def _generate(warn= False):
          prompt = "QuestionOptions"
          response = self.___getResponse(prompt, warn)
          try: 
              message = json.loads(refine_response(response))
              return message["options"], message["answer"]
          except Exception as e:
              print(f"GMAT Verbal, Error: message received for simpleQuestion(generate_questionOptions): {response}\nError: {str(e)}")
              return None
      result_options, result_answer = self._retry_generate(_generate)
      return result_options, result_answer