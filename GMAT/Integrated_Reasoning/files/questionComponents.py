import json, re, os, time
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
max_retries = 3

class GI: 
    def __init__(self, llm, system_instructions, prompt):
        self.startTime = time.time()
        self.requestCounts = 0
        self.llm = llm
        self.prompt = prompt
        self.chat = self.llm.chats.create(
            model = os.getenv("MODEL"),
            config = types.GenerateContentConfig(
                system_instruction = system_instructions
         ))

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
        def _generate(warn= False):
            prompt = f"Mode: QuestionGraph\nPrompt: {self.prompt}\nreturn: `graph`"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message
            except Exception as e:
                print(f"GMAT GI, Error: message received for questionGraph is:\n{response}\n Error: {str(e)}")
                return None
        result_graph = self._retry_generate(_generate)
        return result_graph

    def generate_questionText(self):
        def _generate(warn= False):
            prompt = "Mode: QuestionText return: `question`"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["question"]
            except Exception as e:
                print(f"GMAT GI, Error: message received for questionText is: \n {response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionTitle(self):
        def _generate(warn= False):
            prompt = "Mode: QuestionTitle return: `title`"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(f"GMAT GI, Error: message received for questionTitle is: {response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionSolution(self):
        def _generate(warn= False):
            prompt = "Mode: QuestionSolution return: `solution`"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["solution"]
            except Exception as e:
                print(f"GMAT GI, Error: message received for questionSolution is: {response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionOptions(self):
        def _generate(warn= False):
            prompt = "Mode: QuestionOptions return: `options`, `answer`"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["options"], message["answer"]
            except Exception as e:
                print(f"GMAT GI, Error: message received for questionOptions is: {response}\nError: {str(e)}")
                return None
        result_options, result_answer = self._retry_generate(_generate)
        return result_options, result_answer

class MSR: 
    def __init__(self, llm, system_instructions, prompt):
        self.startTime = time.time()
        self.requestCounts = 0
        self.llm = llm
        self.prompt = prompt
        self.temp_prompt = None
        self.chat = self.llm.chats.create(
            model = os.getenv("MODEL"),
            config = types.GenerateContentConfig(
                system_instruction = system_instructions
        ))

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
                print(f"Error in attempt {attempt + 1}: {last_error}\n\ngot result value: {result}")
        
        if last_error:
            print(f"All attempts failed. Last error: {last_error}")
            return None
        
    def generate_SourceInfo(self, prompt):
        self.temp_prompt = prompt
        def _generate(warn= False):
            response = self.___getResponse(self.temp_prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message
            except Exception as e:
                print(f"GMAT MSR, Error received for SourceInfo is: \n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_MainQuestionTitle(self):
        def _generate(warn= False):
            prompt = "MainQuestionTitle (based on the the given question data what wuold be a unique question title of complete Multi Source Reasoning question)"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(f"GMAT MSR, Error: message received for MainQuestionTitle is:\n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionText(self, prompt):
        self.temp_prompt = prompt
        def _generate(warn= False):
            response = self.___getResponse(self.temp_prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["question"]
            except Exception as e:
                print(f"GMAT MSR, Error: message received for QuestionText generation is:\n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionTitle(self, prompt):
        self.temp_prompt = prompt
        def _generate(warn= False):
            response = self.___getResponse(self.temp_prompt, warn)
            try: 
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(f"GMAT MSR, Error: message received for QuestionTitle generation is:\n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionSolution(self, prompt):
        self.temp_prompt = prompt
        def _generate(warn= False):
            response = self.___getResponse(self.temp_prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["solution"]
            except Exception as e:
                print(f"GMAT MSR, Error: message received for QuestionSolution generation is:\n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionOptions(self, prompt, question_style):
        self.temp_prompt = [prompt, question_style]
        def _generate(warn= False):
            prompt = self.temp_prompt[0]
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                question_style= self.temp_prompt[1]
                if question_style == "MCQ (5 options MCQ)":
                    return message["options"], message["answer"]
                else:
                    return message["options"]
            except Exception as e:
                print(f"GMAT MSR, Error: message received for QuestionOptions is: \n{response}\nError: {str(e)}")
                return None
        if question_style == "MCQ (5 options MCQ)":
            result_options, result_answer = self._retry_generate(_generate)
            return result_options, result_answer
        result = self._retry_generate(_generate)
        return result

class TA:
    def __init__(self, llm, system_instructions, prompt):
        self.startTime = time.time()
        self.requestCounts = 0
        self.llm = llm
        self.prompt = prompt

        self.temp_data = None
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

    def generate_QuestionTable(self, no_rows, no_cols):
        self.temp_data = [no_rows, no_cols]
        def _generate(warn= False):
            no_rows = self.temp_data[0]
            no_cols = self.temp_data[1]
            prompt  = f"QuestionTable, no_rows: {no_rows}, no_cols: {no_cols}; InputPrompt: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["tables"]
            except Exception as e:
                print(f"GMAT TA, Error: message received for QuestionTable is:\n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionText(self):
        def _generate(warn= False):
            prompt = f"QuestionText"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["question"]
            except Exception as e:
                print(f"GMAT TA, Error: message received for QuestionText is: \n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionTitle(self):
        def _generate(warn= False):
            prompt = "QuestionTitle"
            response = self.___getResponse(prompt, warn)
            try: 
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(f"GMAT TA, Error: message received for QuestionTitle is: \n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionOptions(self):
        def _generate(warn= False):
            prompt = f"QuestionOptions"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["options"], message["answer"]
            except Exception as e:
                print(f"GMAT TA, Error: message received for QuestionOptions is: \n{response}\nError: {str(e)}")
                return None
        result_options, result_answer = self._retry_generate(_generate)
        return result_options, result_answer
    
    def generate_QuestionSolution(self):
        def _generate(warn= False):
            prompt = "QuestionSolution"
            response = self.___getResponse(prompt, warn)
            try:
                message= json.loads(refine_response(response))
                return message["solution"]
            except Exception as e:
                print(f"GMAT TA, Error: message received for QuestionSolution is: \n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

class TPA:
    def __init__(self, llm, system_isntruction, prompt):
        self.llm = llm
        self.prompt = prompt
        self.max_retries = 3
        self.startTime = time.time()
        self.requestCounts = 0
        self.chat = self.llm.chats.create(
            model = os.getenv("MODEL"),
            config = types.GenerateContentConfig(
                system_instruction = system_isntruction
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
        
    def generate_ParentQuestionContent(self):
        def _generate(warn = False):
            prompt = f"ParentQuestionContent: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["content"]
            except Exception as e:
                print(f"GMAT TPA, Error message: received for ParentQuestionContent is: \n{response}\nError: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result

    def generate_QuestionText(self, difficulties):
        def _generate(warn= False):
            questions = []
            for i in range(1, 3):
                prompt = f"Question{i}: difficulty Level:{difficulties[i-1]} "
                response  = self.___getResponse(prompt, warn)
                try:
                    message = json.loads(refine_response(response))
                    questions.append(message["question"])
                except Exception as e:
                    print(f"GMAT TPA, Error message: received for QuestionText:\n{response}\nError: {str(e)}")
                    return None
            return questions
        
        result = self._retry_generate(_generate)
        return result if result else []

    def generate_QuestionTitle(self):
        def _generate(warn= False):
            prompt = "QuestionTitle"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(f"GMAT TPA, Error received in QuestionTitle: {response}\nError: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result

    def generate_QuestionSolution(self):
        def _generate(warn= False):
            solutions = []
            for i in range(1,3):
                prompt = f"QuestionSolution {i}"
                response = self.___getResponse(prompt, warn)
                try:
                    message = json.loads(refine_response(response))
                    solutions.append(message["solution"])
                except:
                    print(f"GMAT TPA, Error: message received for QuestionSolution is: \n{response[0].content[0].text.value}\n\n")
                    return None
            return solutions


        result = self._retry_generate(_generate)
        return result 

    def generate_QuestionOptions(self):
        def _generate(warn=False):
            prompt = "QuestionOptions"
            response = self.___getResponse(prompt, warn)
            try:
                
                message = json.loads(refine_response(response))
                if message.get("options") and message.get("answer"):
                    return message["options"], message["answer"]
                print(f"GMAT TPA,didn't get proper options and answers, here is how the complete message looks like:\n{message}")
                return None
            except Exception as e:
                print(f"GMAT TPA, Error: message received for QuestionOptions is: \n{response}\nError:{str(e)}")
                return None
            
        result = self._retry_generate(_generate)
        return result
