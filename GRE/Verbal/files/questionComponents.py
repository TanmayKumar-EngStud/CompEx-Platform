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
max_retries = 3
class ParentChildQuestion:
   def __init__(self, llm, system_instructions, global_state, prompt, lock):
      self.global_state = global_state
      self.lock = lock
      self.llm = llm
      self.prompt = prompt
      self.startTime = time.time()
      self.requestCounts = 0
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
      
   def generate_passages(self):
      def _generate(warn = False):
      #region 🔄 getting passage count
         if "rc-s" in self.prompt.lower():
            total_passage_count = 2
         elif "rc-m" in self.prompt.lower():
            total_passage_count = 3
         elif "rc-l" in self.prompt.lower():
            total_passage_count = 4
         else:
            total_passage_count = 0
            print(f"GRE_Verbal: this is self.prompt: {self.prompt} thus total_passage_count didn't worked")
            return None
      #endregion
         
         passages = []
         for passage_number in range(total_passage_count):
            prompt = f"ParentQuestion: {self.prompt} generate passage {passage_number+1} of {total_passage_count}"
            response = self.___getResponse(prompt)
            try:
               message = json.loads(refine_response(response))
               passages.append(message[f'passage'])
            except Exception as e:
               print(f"GRE Verbal, Error in generating passage \nPassage:{passage_number} of {total_passage_count}: {str(e)}\nreceived response: \n{response}")
               return None
         return passages
      result = self._retry_generate(_generate)
      return result if result else ["error generating question passages"]
   def generate_parentTitle(self):
      def _generate(warn= False):
         prompt = f"ParentTitle:"
         response = self.___getResponse(prompt,warn)
         try:
            message = json.loads(refine_response(response))
            return message.get("title", "error key 'title' not found in GRE Verbal (ParentChild question generation)")
         except Exception as e:
            print(f"Failed json parsing for question title here is how the response looked like : {response}")
            print(f"error: {str(e)}")
      result = self._retry_generate(_generate)
      return result if result else "error generating parent question"
   def generate_childQuestion(self, index, child_prompt =""):
      def _generate(warn = False):
         prompt = f"ChildQuestion: {index} of {child_prompt}"
         response = self.___getResponse(prompt, warn)
         try:
            message = json.loads(refine_response(response))
            return message.get("question", f"error generating childQuestion for {self.prompt}")
         except Exception as e:
            print(f"GRE Verbal, error in generate_childQuestion: {str(e)}")
            return None
      result = self._retry_generate(_generate)
      return result if result else "Error failed to generate childQuestion"
   def generate_childQuestionTitle(self, index):
      def _generate(warn = False):
         prompt = f"ChildQuestionTitle: {index}"
         response = self.___getResponse(prompt, warn)
         try:
            message = json.loads(refine_response(response))
            return message.get("title", f"error generating childQuestionTitle for {self.prompt}")
         except Exception as e:
            print(f"GRE Verbal, error in generate_childQuestionTitle: {str(e)}")
            return None
      result = self._retry_generate(_generate)
      return result if result else "Error failed to generate childQuestionTitle"
   def generate_childOptions(self, index):
      def _generate(warn = False):
         prompt = f"ChildOptions: {index}"
         response = self.___getResponse(prompt, warn)
         try:
            message = json.loads(refine_response(response))
            options = message.get("options", f"error generating childOptions for {self.prompt}")
            answer = message.get("answer", f"error generating childOptions for {self.prompt}")
            return options, answer
         except Exception as e:
            print(f"GRE Verbal, error in generate_childOptions: {str(e)}")
            return None
      options, answer = self._retry_generate(_generate)
      return options, answer
   def generate_childSolution(self, index):
      def _generate(warn = False):
         prompt = f"ChildSolution: {index}"
         response = self.___getResponse(prompt, warn)
         try:
            message = json.loads(refine_response(response))
            return message.get("solution", f"parent child solution value is not getting captured {self.prompt}")
         except Exception as e:
            print(f"GRE Verbal, error in generate_childSolution: {str(e)}")
            return None
      result = self._retry_generate(_generate)
      return result if result else "Error failed to generate childSolution"
   
class SimpleQuestion:
   def __init__(self, llm, system_instructions, global_state, prompt, lock) -> None:
      self.global_state = global_state
      self.lock = lock
      self.llm = llm
      self.prompt = prompt
      self.startTime = time.time()
      self.requestCounts = 0
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
      func_name = func.__name__
      for attempt in range(max_retries):
         try:
            result = func(*args, True if attempt else False)
            if result:
               return result
            print(f"🚩 {func_name} has failed to return response - attempt {attempt+1}/{max_retries}")
            print(f"\tReason: Function returned None")
         except Exception as e: 
            print(f"🏳️ {func_name} failed in even attempting [SimpleQuestion-GRE Verbal]because: {str(e)}")
      return None

   def generate_questionText(self):
      def _generate(warn = False):
         prompt = f"QuestionText: {self.prompt}"
         response = self.___getResponse(prompt, warn)
         try:
            message =json.loads(refine_response(response))
            if "cr" in self.prompt.lower():
               if not message.get("passage"):
                  raise Exception("Missing 'passage' field in response")
               if not message.get("question"):
                  raise Exception("Missing 'question' field in response")
               return message["passage"], message["question"]
            res = message.get('question', f'question keyword is not getting captured {self.prompt}')
            return res
         except Exception as e:
            print(f"GRE verbal, error in generate_questionText: {str(e)}")
            print(f"getting this response value: {response}")
            return None

      if "cr" in self.prompt.lower():
         passage, question = self._retry_generate(_generate)
         return passage, question
      else:
         question = self._retry_generate(_generate)
         return question
   def generate_questionTitle(self):
      def _generate(warn = False):
         prompt = f"QuestionTitle"
         response = self.___getResponse(prompt, warn)
         try:
            message = json.loads(refine_response(response))
            return message.get('title', f"simple question title value is not getting captured {self.prompt}")
         except Exception as e:
            print(f"GRE Verbal, error in generate_questionTitle: {str(e)}")
            print(f"getting this as a response value: {response}")
         return None
      result = self._retry_generate(_generate)
      return result if result else "Error failed to generate questionTitle"
   def generate_questionSolution(self):
      def _generate(warn = False):
         prompt = f"QuestionSolution"
         response = self.___getResponse(prompt, warn)
         try:
            message = json.loads(refine_response(response))
            return message.get('solution', f"solution value is not getting captured {self.prompt}")
         except Exception as e:
            print(f"GRE Verbal, error in generate_childSolution: {str(e)}")
            print(f"this is the response that is being captured: {response}")
         return None
      solution = self._retry_generate(_generate)
      return solution
   def generate_questionOptions(self, num_options):
      def _generate(warn= False):
         prompt = f"QuestionOptions, number of options: {num_options}"
         response = self.___getResponse(prompt, warn)
         try:
            message = json.loads(refine_response(response))
            options = message.get('options', [])
            answer = message.get('answer', [])
            return options, answer
         except Exception as e:
            print("Failed to create question options and answers in simpleQuestion")
            print(f"this is the response that was returned {response}")
         return None
      options, answer = self._retry_generate(_generate)
      return options, answer
