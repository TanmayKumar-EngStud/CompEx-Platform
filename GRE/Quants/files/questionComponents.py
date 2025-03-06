import json, re, time, os
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
               # it reached here because it has backslashes.
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

warning = "\nWARNING: please retry this, your output should strictly follow json format so that python program can capture question component properly, use (`) symbol instead of single quote and every key and value should be enclosed in double quotes"
max_retries = 3

class ParentChildQuestion:
    def __init__(self, llm, system_instructions, prompt):
        self.llm = llm
        self.startTime = time.time()
        self.requestCounts = 0
        self.prompt = prompt
        self.chat = self.llm.chats.create(
            model = os.getenv("MODEL"),
            config = types.GenerateContentConfig(
                system_instruction = system_instructions
            )
        )
    def ___getResponse(self, prompt, warn= False):
        prompt += (f", {warning}" if warn else "")
        try: 
            self.requestCounts += 1
            presentTime = time.time()
            
            # If we've reached 10 requests, enforce the rate limit
            if self.requestCounts >= 10:
                # Calculate time elapsed since start
                elapsed = presentTime - self.startTime
                
                # If less than 60 seconds have passed, we need to wait
                if elapsed < 60:
                    wait_time = 60 - elapsed + 0.5  # Add a small buffer
                    print(f"RPM limit reached, sleeping for {wait_time} seconds")
                    print(f"Requests: {self.requestCounts}, Elapsed time: {elapsed:.2f}s")
                    time.sleep(wait_time)
                
                # Reset counters after waiting or if 60+ seconds have already passed
                self.startTime = time.time()
                self.requestCounts = 1  # Set to 1 for the current request
            
            response = self.chat.send_message(prompt)
            val = response.text
            return val
        except Exception as e:
            print(f"{prompt}")
            print(f"failed in generating response by self.llm.invoke")
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
      
    def generate_questionGraph(self):
        def _generate(warn = False):
            prompt = f"questionGraph: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                graph = {}
                try:
                    graph = message["graph/table"]
                except Exception as e:
                    graph = message["graph"]
                    print(f"GRE Quants, Warning: message received for generate_questionGraph: received 'graph' instead of 'graph/table'.\n")
                return graph
            except Exception as e:
                print(f"GRE Quants, Error: message received for questionGraph is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result
    def generate_parentTitle(self):
        def _generate(warn = False):
            prompt = f"ParentTitle"
            response = self.___getResponse(prompt, warn)

            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(f"GRE Quants, Error: message received for parentChildQuestion(generate_parentTitle) is: \n{response}\nError: {str(e)}\n\n")
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
                print(f"GRE Quants, Error: message received for parentChildQuestion(generate_childQuestionTitle) is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result
    def generate_childQuestion(self, index, child_prompt=""):
        def _generate(warn = False):
            prompt = f"generate ChildQuestion: {index} of {child_prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["question"]
            except Exception as e:
                print(f"GRE Quants, Error: message received for parentChildQuestion(generate_childQuestion) is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result
    def generate_childQuestion(self, index, child_prompt=""):
        def _generate(warn = False):
            prompt = f"generate ChildQuestion: {index} of {child_prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["question"]
            except Exception as e:
                print(f"GRE Quants, Error: message received for parentChildQuestion(generate_childQuestion) is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result
    def generate_childOptions(self, index):
        def _generate(warn = False):
            prompt = f"ChildOptions: {index}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["options"], message["answer"]
            except Exception as e:
                print(f"GRE Quants, Error: message received for parentChildQuestion(generate_childOptions) is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result
    def generate_childSolution(self, index):
        def _generate(warn = False):
            prompt = f"ChildSolution: {index}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["solution"]
            except Exception as e:
                print(f"GRE Quants, Error: message received for parentChildQuestion(generate_childSolution) is: \n{response[0].content[0].text.value}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result

class SimpleQuestion:
    def __init__(self, llm, system_instructions, prompt):
        self.llm = llm
        self.startTime = time.time()
        self.requestCounts = 0
        self.prompt = prompt
        self.chat = self.llm.chats.create(
            model = os.getenv("MODEL"),
            config = types.GenerateContentConfig(
                system_instruction = system_instructions
            )
        )

    def ___getResponse(self, prompt, warn= False):
        prompt += (f", {warning}" if warn else "")
        try: 
            self.requestCounts += 1
            presentTime = time.time()
            
            # If we've reached 10 requests, enforce the rate limit
            if self.requestCounts >= 10:
                # Calculate time elapsed since start
                elapsed = presentTime - self.startTime
                
                # If less than 60 seconds have passed, we need to wait
                if elapsed < 60:
                    wait_time = 60 - elapsed + 0.5  # Add a small buffer
                    print(f"RPM limit reached, sleeping for {wait_time} seconds")
                    print(f"Requests: {self.requestCounts}, Elapsed time: {elapsed:.2f}s")
                    time.sleep(wait_time)
                
                # Reset counters after waiting or if 60+ seconds have already passed
                self.startTime = time.time()
                self.requestCounts = 1  # Set to 1 for the current request
            
            response = self.chat.send_message(prompt)
            val = response.text
            return val
        except Exception as e:
            print(f"{prompt}")
            print(f"failed in generating response by self.llm.invoke")
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
        
    def generate_questionText(self):
        def _generate(warn = False):
            prompt = f"QuestionText: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["question"]
            except Exception as e:
                print(f"GRE Quants, Error: message received for questionText is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result
    
    def generate_questionTitle(self):
        def _generate(warn = False):
            prompt = f"QuestionTitle"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(f"GRE Quants, Error: message received for questionTitle is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result
    
    def generate_questionSolution(self, isNE = False):
        def _generate(warn = False):
            prompt = f"QuestionSolution"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                if isNE:
                    return message["solution"], float(message["answer"])
                else:
                    return message["solution"]
            except Exception as e:
                print(f"GRE Quants, Error: message received for questionSolution is: \n{response}\nError: {str(e)}\n\n")
                return None
        if isNE:
            result_solution, result_answer = self._retry_generate(_generate)
            return result_solution, result_answer
        else:
            result = self._retry_generate(_generate)
            return result

    def generate_questionOptions(self):
        def _generate(warn = False):
            prompt = f"QuestionOptions"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["options"], message["answer"]
            except Exception as e:
                print(f"GRE Quants, Error: message received for questionOptions is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result

class DataSufficiencyQuestion:
    def __init__(self, llm, system_instructions, prompt):
        self.llm = llm
        self.startTime = time.time()
        self.requestCounts = 0
        self.prompt = prompt
        self.chat = self.llm.chats.create(
            model = os.getenv("MODEL"),
            config = types.GenerateContentConfig(
                system_instruction = system_instructions
            )
        )
    
    def ___getResponse(self, prompt, warn= False):
        prompt += (f", {warning}" if warn else "")
        try: 
            self.requestCounts += 1
            presentTime = time.time()
            
            # If we've reached 10 requests, enforce the rate limit
            if self.requestCounts >= 10:
                # Calculate time elapsed since start
                elapsed = presentTime - self.startTime
                
                # If less than 60 seconds have passed, we need to wait
                if elapsed < 60:
                    wait_time = 60 - elapsed + 0.5  # Add a small buffer
                    print(f"RPM limit reached, sleeping for {wait_time} seconds")
                    print(f"Requests: {self.requestCounts}, Elapsed time: {elapsed:.2f}s")
                    time.sleep(wait_time)
                
                # Reset counters after waiting or if 60+ seconds have already passed
                self.startTime = time.time()
                self.requestCounts = 1  # Set to 1 for the current request
            
            response = self.chat.send_message(prompt)
            val = response.text
            return val
        except Exception as e:
            print(f"{prompt}")
            print(f"failed in generating response by self.llm.invoke")
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
        
    def generate_questionText(self):
        def _generate(warn = False):
            prompt = f"QuestionText: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["passage"], message["statements"], message["question"]
            except Exception as e:
                print(f"GRE Quants, Error: message received for questionText is: \n{response}\nError: {str(e)}\n\n")
                return None
        result_passage, result_statements, result_question = self._retry_generate(_generate)
        return result_passage, result_statements, result_question

    def generate_questionTitle(self):
        def _generate(warn = False):
            prompt = f"QuestionTitle"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(f"GRE Quants, Error: message received for questionTitle is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result
    
    def generate_questionSolution(self):
        def _generate(warn = False):
            prompt = f"QuestionSolution"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["solution"], str(message["answer"])
            except Exception as e:
                print(f"GRE Quants, Error: message received for questionSolution is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionOptions(self):
        def _generate(warn = False):
            prompt = f"QuestionOptions"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["options"], message["answer"]
            except Exception as e:
                print(f"GRE Quants, Error: message received for questionOptions is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result
