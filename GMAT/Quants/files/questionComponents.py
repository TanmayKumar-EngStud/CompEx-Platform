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

class SimpleQuestion:
    def __init__(self, llm, system_instructions, global_state, lock, prompt):
        self.lock = lock
        self.global_state =  global_state
        self.llm = llm
        self.prompt = prompt
        self.max_retries = 3
        self.chat = self.llm.chats.create(
            model = os.getenv("MODEL"),
            config = types.GenerateContentConfig(
                system_instruction = system_instructions
            )
        )

    def ___getResponse(self, prompt, warn= False):
        prompt += (f", {warning}" if warn else "")
        try:
            self.global_state["request_count"] += 1
            presentTime = time.time()
            
            # If we've reached 10 requests, enforce the rate limit
            if self.global_state["request_count"] >= 10:
                # Calculate time elapsed since start
                elapsed = presentTime - self.global_state["start_time"]
                
                # If less than 60 seconds have passed, we need to wait
                if elapsed < 60:
                    wait_time = 60 - elapsed + 0.5  # Add a small buffer
                    print(f"RPM limit reached, sleeping for {wait_time} seconds")
                    print(f"Requests: {self.global_state['request_count']}, Elapsed time: {elapsed:.2f}s")
                    time.sleep(wait_time)
                
                # Reset counters after waiting or if 60+ seconds have already passed
                self.global_state["start_time"] = time.time()
                self.global_state["request_count"] = 1  # Set to 1 for the current request
            
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
        for attempt in range(self.max_retries):
            try:
                result = func(*args, warn= True if attempt else False)
                if result:  # If we got any non-None result, return it
                    return result
                print(f"Retrying {func.__name__} - attempt {attempt + 1}/{self.max_retries}")
            except Exception as e:
                last_error = str(e)
                print(f"Error in attempt {attempt + 1}: {last_error}")
        
        # If we get here, all attempts failed
        if last_error:
            print(f"All attempts failed. Last error: {last_error}")
        return None

    def generate_questionText(self, input_data):
        def _generate(warn = False):
            prompt = f"QuestionText: {input_data}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                if message.get("question"):
                    return message["question"]
                return None
            except Exception as e:
                print(f"GMAT Quants, Error in generate_questionText: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result if result else ("error generating question text", "")

    def generate_questionTitle(self):
        def _generate(warn= False):
            prompt = f"QuestionTitle "
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message.get("title", "")
            except Exception as e:
                print(f"GMAT Quants, Error in generate_questionTitle: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result if result else ""

    def generate_questionSolution(self):
        def _generate(warn = False):
            prompt = f"QuestionSolution"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))    
                return message.get("solution", "error solution component not found")
            except Exception as e:
                print(f"GMAT Quants, Error in generate_questionSolution: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result if result else ""

    def generate_questionOptions(self):
        def _generate(warn= False):
            prompt = f"QuestionOptions"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                if message.get("options") and message.get("answer"):
                    return message["options"], message["answer"]
                return None
            except Exception as e:
                print(f"GMAT Quants, Error in generate_questionOptions: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result if result else ({}, "")

class DataSufficiencyQuestion:
    def __init__(self, llm, system_instructions, global_state, lock, prompt):
        self.lock = lock
        self.global_state = global_state
        self.llm = llm
        self.prompt = prompt
        self.max_retries = 3
        self.chat = self.llm.chats.create(
            model = os.getenv("MODEL"),
            config = types.GenerateContentConfig(
                system_instruction = system_instructions
            )
        )

    def ___getResponse(self, prompt, warn= False):
        prompt += (f", {warning}" if warn else "")
        try:
            self.global_state["request_count"] += 1
            presentTime = time.time()
            
            # If we've reached 10 requests, enforce the rate limit
            if self.global_state["request_count"] >= 10:
                # Calculate time elapsed since start
                elapsed = presentTime - self.global_state["start_time"]
                
                # If less than 60 seconds have passed, we need to wait
                if elapsed < 60:
                    wait_time = 60 - elapsed + 0.5  # Add a small buffer
                    print(f"RPM limit reached, sleeping for {wait_time} seconds")
                    print(f"Requests: {self.global_state['request_count']}, Elapsed time: {elapsed:.2f}s")
                    time.sleep(wait_time)
                
                # Reset counters after waiting or if 60+ seconds have already passed
                self.global_state["start_time"] = time.time()
                self.global_state["request_count"] = 1  # Set to 1 for the current request
            
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
        for attempt in range(self.max_retries):
            try:
                result = func(*args, warn= True if attempt else False)
                if result:  # If we got any non-None result, return it
                    return result
                print(f"Retrying {func.__name__} - attempt {attempt + 1}/{self.max_retries}")
            except Exception as e:
                last_error = str(e)
                print(f"Error in attempt {attempt + 1}: {last_error}")
        
        # If we get here, all attempts failed
        if last_error:
            print(f"All attempts failed. Last error: {last_error}")
        return None
    
    def generate_questionGraph(self):
        def _generate(warn = False):
            prompt = f"questionGraph: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["graph/table"]
            except Exception as e:
                print(f"GMAT Quants, Error: message received for questionGraph is: \n{response}") 
                return None
        result = self._retry_generate(_generate)
        return result
    
    def generate_questionText(self):
        def _generate(warn= False):
            prompt = f"QuestionText: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["question_passage"], message["statements"], message["question"]
            except Exception as e:
                print(f"GMAT Quants, Error message received for questionText is: {str(e)}")
                return None
        result_message_question_passage, result_statements, result_question = self._retry_generate(_generate)
        return result_message_question_passage, result_statements, result_question

    def generate_questionTitle(self):
        def _generate(warn= False):
            prompt = f"QuestionTitle"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(f"GMAT Quants, error in generate_questionTitle: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result
    
    def generate_questionSolution(self):
        def _generate(warn = False):
            prompt = f"questionSolution"
            response = self.___getResponse(prompt, warn)
            try:
                message= json.loads(refine_response(response))
                return message["solution"], str(message["answer"])
            except Exception as e:
                print(f"GMAT Quants, Error: message received for questionSolution is: \n{response}, \nError: {str(e)}")
                return None
        result_solution, result_answer = self._retry_generate(_generate)
        return result_solution, result_answer
