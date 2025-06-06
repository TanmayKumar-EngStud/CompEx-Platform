import json
import re
import time
import os
from google.genai import types


def refine_response(response_text):
    """
    refines json responses, wrapped in json```{block}``` and  properly handles with new line inside the values and keys.
    """
    def remove_tailing_commas(string):
        # remove tailing commas
        # }, -> } ; ], -> ]
        string = re.sub(r',(\s*})', r'\1', string)
        string = re.sub(r',(\s*])', r'\1', string)
        # {' -> {" ; [' -> [" ; '} -> "} ; '] -> "] ; '\s*: -> "\s*:
        string = re.sub(r"(\[\s*)'", r'\1"', string)
        string = re.sub(r"(\{\s*)'", r'\1"', string)
        string = re.sub(r"'(\s*\])", r'"\1', string)
        string = re.sub(r"'(\s*\})", r'"\1', string)
        string = re.sub(r"'(\s*:)", r'"\1', string)

        # if not enclosed in double quotes
        # *'\s*, -> *"\s*, ;  ,\s*'* -> ,\s*"* ;
        string = re.sub(r"([a-zA-Z0-9\s!.`]\s*)'(\s*,)", r'\1"\2', string)
        string = re.sub(r"(,\s*)'(\s*[a-zA-Z0-9])", r'\1"\2', string)
        return string

    def preprocessing_string(match):
        value = match.group(0)
        value = value.replace("\n", "<br>")
        value = value.replace("\t", "<t>")
        value = value.replace("\f", "<f>")
        value = value.replace("\\f", "<f>")
        value = value.replace("\\t", "<t>")
        value = value.replace("\i", "<i>")
        value = value.replace("\s", "<s>")
        value = value.replace("\pi", "<pi>")
        value = re.sub(r"\\(.)", r"\\\\\1", value)
        return value

    def postprocessing_string(json_data):
        for key, value in json_data.items():
            if isinstance(value, str):
                json_data[key] = value.replace("<br>", "\n")
                json_data[key] = json_data[key].replace("<t>", "\\t")
                json_data[key] = json_data[key].replace("<f>", "\\f")
                json_data[key] = json_data[key].replace("<i>", "\\i")
                json_data[key] = json_data[key].replace("<s>", "\\s")
                json_data[key] = json_data[key].replace("<pi>", "\\pi")
        return json.dumps(json_data)

    if not response_text:
        return response_text

    pattern = r'"(.*?)"'
    new_text = re.search(r"```json\n(.*?)```",
                         response_text, re.DOTALL).group(1)
    key_and_values = re.findall(pattern, new_text, re.DOTALL)

    for key_and_value in key_and_values:
        if "\n" in key_and_value:
            proper_key_and_value = key_and_value.replace("\n", "\\n")
            new_text = new_text.replace(
                f'"{key_and_value}"', f'"{proper_key_and_value}"')
    try:
        data = json.loads(new_text)
        return json.dumps(data, indent=2)
    except json.JSONDecodeError as e:
        try:
            new_text = re.search(
                r"```json\n(.*?)```",
                response_text,
                re.DOTALL
            ).group(1)
            new_text = remove_tailing_commas(new_text)
            pattern = r'"(.*?)"'
            text = re.sub(
                pattern,
                preprocessing_string,
                new_text,
                flags=re.DOTALL
            )
            pseudo_data = json.loads(text)
            post_pseudo_data = postprocessing_string(pseudo_data)
            data = json.loads(post_pseudo_data)
            return json.dumps(data, indent=2)
        except Exception as e:
            print(f"Error in refining response: {str(e)}")
            with open(os.path.join(os.path.dirname(__file__), "error_response.txt"), "+a") as f:
                f.write(response_text)
                f.write("\n")
            return None


warning = "\nWARNING: please retry this, your output should strictly follow json format so that python program can capture question component properly, use (`) symbol instead of single quote and every key and value should be enclosed in double quotes"


class SimpleQuestion:
    def __init__(self, llm, system_instructions, global_state, lock, prompt):
        self.lock = lock
        self.global_state = global_state
        self.llm = llm
        self.prompt = prompt
        self.max_retries = 3
        self.chat = self.llm.chats.create(
            model=os.getenv("MODEL"),
            config=types.GenerateContentConfig(
                system_instruction=system_instructions
            )
        )

    def ___getResponse(self, prompt, warn=False):
        prompt += (f", {warning}" if warn else "")
        
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.global_state["start_time"]
            
            # Reset window if more than 60 seconds have passed
            if elapsed >= 60:
                self.global_state["start_time"] = current_time
                self.global_state["request_count"] = 0
                elapsed = 0
            
            # Check if we're at the limit
            if self.global_state["request_count"] >= 9:  # Use 9 instead of 10 for safety margin
                wait_time = 60 - elapsed + 1  # Add 1 second buffer
                if wait_time > 0:
                    print(f"Rate limit safety: waiting {wait_time:.1f}s (requests: {self.global_state['request_count']}, elapsed: {elapsed:.1f}s)")
                    time.sleep(wait_time)
                    # Reset after waiting
                    self.global_state["start_time"] = time.time()
                    self.global_state["request_count"] = 0
            
            # Increment request count
            self.global_state["request_count"] += 1
            
        try:
            response = self.chat.send_message(prompt)
            val = response.text
            return val
        except Exception as e:
            print(f"{prompt}")
            print(f"failed in generating response by self.llm.invoke")
            print(f"{str(e)}")
            # On error, wait longer before retry
            with self.lock:
                current_time = time.time()
                elapsed = current_time - self.global_state["start_time"]
                if elapsed < 60:
                    wait_time = 60 - elapsed + 2  # Extra buffer on error
                    time.sleep(wait_time)
                self.global_state["start_time"] = time.time()
                self.global_state["request_count"] = 0
            return None

    def _retry_generate(self, func, *args):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                result = func(*args, warn=True if attempt else False)
                if result:  # If we got any non-None result, return it
                    return result
                print(
                    f"Retrying {func.__name__} - attempt {attempt + 1}/{self.max_retries}")
            except Exception as e:
                last_error = str(e)
                print(f"Error in attempt {attempt + 1}: {last_error}")

        # If we get here, all attempts failed
        if last_error:
            print(f"All attempts failed. Last error: {last_error}")
        return None

    def generate_questionText(self, input_data):
        def _generate(warn=False):
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
        def _generate(warn=False):
            prompt = f"QuestionTitle "
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message.get("title", "")
            except Exception as e:
                print(
                    f"GMAT Quants, Error in generate_questionTitle: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result if result else ""

    def generate_questionSolution(self):
        def _generate(warn=False):
            prompt = f"QuestionSolution"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message.get("solution", "error solution component not found")
            except Exception as e:
                print(
                    f"GMAT Quants, Error in generate_questionSolution: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result if result else ""

    def generate_questionOptions(self):
        def _generate(warn=False):
            prompt = f"QuestionOptions"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                if message.get("options") and message.get("answer"):
                    return message["options"], message["answer"]
                return None
            except Exception as e:
                print(
                    f"GMAT Quants, Error in generate_questionOptions: {str(e)}")
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
            model=os.getenv("MODEL"),
            config=types.GenerateContentConfig(
                system_instruction=system_instructions
            )
        )

    def ___getResponse(self, prompt, warn=False):
        prompt += (f", {warning}" if warn else "")
        
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.global_state["start_time"]
            
            # Reset window if more than 60 seconds have passed
            if elapsed >= 60:
                self.global_state["start_time"] = current_time
                self.global_state["request_count"] = 0
                elapsed = 0
            
            # Check if we're at the limit
            if self.global_state["request_count"] >= 9:  # Use 9 instead of 10 for safety margin
                wait_time = 60 - elapsed + 1  # Add 1 second buffer
                if wait_time > 0:
                    print(f"Rate limit safety: waiting {wait_time:.1f}s (requests: {self.global_state['request_count']}, elapsed: {elapsed:.1f}s)")
                    time.sleep(wait_time)
                    # Reset after waiting
                    self.global_state["start_time"] = time.time()
                    self.global_state["request_count"] = 0
            
            # Increment request count
            self.global_state["request_count"] += 1
            
        try:
            response = self.chat.send_message(prompt)
            val = response.text
            return val
        except Exception as e:
            print(f"{prompt}")
            print(f"failed in generating response by self.llm.invoke")
            print(f"{str(e)}")
            # On error, wait longer before retry
            with self.lock:
                current_time = time.time()
                elapsed = current_time - self.global_state["start_time"]
                if elapsed < 60:
                    wait_time = 60 - elapsed + 2  # Extra buffer on error
                    time.sleep(wait_time)
                self.global_state["start_time"] = time.time()
                self.global_state["request_count"] = 0
            return None

    def _retry_generate(self, func, *args):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                result = func(*args, warn=True if attempt else False)
                if result:  # If we got any non-None result, return it
                    return result
                print(
                    f"Retrying {func.__name__} - attempt {attempt + 1}/{self.max_retries}")
            except Exception as e:
                last_error = str(e)
                print(f"Error in attempt {attempt + 1}: {last_error}")

        # If we get here, all attempts failed
        if last_error:
            print(f"All attempts failed. Last error: {last_error}")
        return None

    def generate_questionGraph(self):
        def _generate(warn=False):
            prompt = f"questionGraph: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["graph/table"]
            except Exception as e:
                print(
                    f"GMAT Quants, Error: message received for questionGraph is: \n{response}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionText(self):
        def _generate(warn=False):
            prompt = f"QuestionText: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["question_passage"], message["statements"], message["question"]
            except Exception as e:
                print(
                    f"GMAT Quants, Error message received for questionText is: {str(e)}")
                return None
        result_message_question_passage, result_statements, result_question = self._retry_generate(
            _generate)
        return result_message_question_passage, result_statements, result_question

    def generate_questionTitle(self):
        def _generate(warn=False):
            prompt = f"QuestionTitle"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(
                    f"GMAT Quants, error in generate_questionTitle: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionSolution(self):
        def _generate(warn=False):
            prompt = f"questionSolution"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["solution"], str(message["answer"])
            except Exception as e:
                print(
                    f"GMAT Quants, Error: message received for questionSolution is: \n{response}, \nError: {str(e)}")
                return None
        result_solution, result_answer = self._retry_generate(_generate)
        return result_solution, result_answer
