import json
import re
import time
import os
from google.genai import types


def refine_response(response_text):
    """
    refines json responses, wrapped in json```{block}``` and  properly handles with new line inside the values and keys.
    """
    if not response_text or response_text.strip() == "":
        print("Warning: Empty response received")
        return '{"error": "Empty response received"}'

    def clean_json_string(text):
        """Clean JSON string to fix common formatting issues"""
        # Remove any leading/trailing whitespace and non-JSON content
        text = text.strip()

        # Remove any markdown code block indicators
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```', '', text, flags=re.MULTILINE)

        # Normalize whitespace by joining all lines
        lines = text.split('\n')
        cleaned_text = ''
        for line in lines:
            cleaned_line = line.strip()
            if cleaned_line:
                cleaned_text += cleaned_line + ' '

        cleaned_text = cleaned_text.strip()
        
        # Try to parse the cleaned JSON
        try:
            json.loads(cleaned_text)
            return cleaned_text
        except json.JSONDecodeError:
            return None

    def fix_br_tags_in_json(json_string):
        """Parse JSON and fix <br> tags to proper newlines"""
        try:
            # Parse the JSON
            data = json.loads(json_string)

            # Recursively fix <br> tags in all string values
            def fix_br_recursive(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        obj[key] = fix_br_recursive(value)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        obj[i] = fix_br_recursive(item)
                elif isinstance(obj, str):
                    # Replace <br> with actual newlines
                    obj = obj.replace('<br>', '\n')
                return obj

            # Fix the data and return as formatted JSON
            fixed_data = fix_br_recursive(data)
            return json.dumps(fixed_data, indent=2)

        except json.JSONDecodeError:
            return json_string
        except Exception:
            return json_string

    # Extract JSON from various formats
    new_text = None

    # Pattern 1: ```json\n...\n```
    markdown_match = re.search(r"```json\s*\n(.*?)\n\s*```", response_text, re.DOTALL)
    if markdown_match:
        try:
            group_text = markdown_match.group(1)
            if group_text and group_text.strip():
                new_text = group_text.strip()
        except (IndexError, AttributeError):
            pass

    # Pattern 2: ```\n{...}\n```
    if not new_text:
        json_block_match = re.search(r"```\s*\n(\{.*?\})\n\s*```", response_text, re.DOTALL)
        if json_block_match:
            try:
                group_text = json_block_match.group(1)
                if group_text and group_text.strip():
                    new_text = group_text.strip()
            except (IndexError, AttributeError):
                pass

    # Pattern 3: Look for JSON object starting with { - use balanced brace matching
    if not new_text:
        # Find the first opening brace
        start_pos = response_text.find('{')
        if start_pos != -1:
            # Count braces to find the matching closing brace
            brace_count = 0
            end_pos = start_pos
            for i, char in enumerate(response_text[start_pos:], start_pos):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i
                        break
            
            if brace_count == 0:  # Found matching brace
                try:
                    group_text = response_text[start_pos:end_pos + 1]
                    if group_text and group_text.strip():
                        new_text = group_text.strip()
                except Exception:
                    pass

    # Fallback: assume entire response is JSON
    if not new_text:
        new_text = response_text.strip()

    # Clean the JSON string
    new_text = clean_json_string(new_text)
    
    if new_text is None:
        return '{"error": "Failed to parse JSON response"}'

    # Fix <br> tags to proper newlines
    new_text = fix_br_tags_in_json(new_text)

    # Final validation and formatting
    try:
        data = json.loads(new_text)
        return json.dumps(data, indent=2)
    except json.JSONDecodeError:
        return '{"error": "Failed to parse JSON response"}'


warning = "\nCRITICAL ERROR: Your response MUST be valid JSON only. EXAMPLE: {\"solution\": \"text here\"}. No text before/after JSON. No explanations. No markdown. Just pure JSON that can be parsed by json.loads(). Use (`) instead of single quotes inside strings."
max_retries = 3

def is_error_response(message):
    """Check if the parsed JSON is an error response from refine_response"""
    return isinstance(message, dict) and "error" in message and len(message) == 1

def log_detailed_error(context, raw_response, error, expected_keys=None):
    """Log detailed error information for debugging"""
    print("=" * 80)
    print(f"DETAILED ERROR LOG - {context}")
    print("=" * 80)
    print(f"Error: {str(error)}")
    print("-" * 40)
    print("RAW RESPONSE:")
    print(raw_response)
    print("-" * 40)
    print(f"Response type: {type(raw_response)}")
    print(f"Response length: {len(raw_response) if raw_response else 0}")
    if expected_keys:
        print(f"Expected keys: {expected_keys}")
    
    # Try to show what refine_response produces
    try:
        refined = refine_response(raw_response)
        print("REFINED RESPONSE:")
        print(refined)
        print("-" * 40)
        
        # Try to parse the refined response
        try:
            parsed = json.loads(refined)
            print("PARSED JSON KEYS:")
            if isinstance(parsed, dict):
                print(list(parsed.keys()))
                print("PARSED JSON CONTENT:")
                for key, value in parsed.items():
                    print(f"  {key}: {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
            else:
                print(f"Parsed JSON is not a dict, it's: {type(parsed)}")
                print(f"Content: {str(parsed)[:500]}{'...' if len(str(parsed)) > 500 else ''}")
        except Exception as parse_error:
            print(f"FAILED TO PARSE REFINED JSON: {str(parse_error)}")
    except Exception as refine_error:
        print(f"FAILED TO REFINE RESPONSE: {str(refine_error)}")
    
    print("=" * 80)
    print()
max_retries = 3


class ParentChildQuestion:
    def __init__(self, llm, system_instructions, global_state, prompt, lock):
        self.global_state = global_state
        self.lock = lock
        self.llm = llm
        self.prompt = prompt
        self.chat = self.llm.chats.create(
            model=os.getenv("MODEL"),
            config=types.GenerateContentConfig(
                system_instruction=system_instructions,
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True
                )
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
            # Use 9 instead of 10 for safety margin
            if self.global_state["request_count"] >= 9:
                wait_time = 60 - elapsed + 1  # Add 1 second buffer
                if wait_time > 0:
                    print(
                        f"Rate limit safety: waiting {wait_time:.1f}s (requests: {self.global_state['request_count']}, elapsed: {elapsed:.1f}s)")
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
        for attempt in range(max_retries):
            try:
                result = func(*args, warn=True if attempt else False)
                if result:
                    return result
                print(
                    f"Retrying {func.__name__} - attempt {attempt + 1}/ {max_retries}")
            except Exception as e:
                last_error = str(e)
                print(f"Error in attempt {attempt + 1}: {last_error}")

        if last_error:
            print(f"All attempts failed. Last error: {last_error}")
            return None

    def generate_questionGraph(self):
        def _generate(warn=False):
            prompt = f"questionGraph: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                graph = {}
                try:
                    graph = message["graph/table"]
                except Exception as e:
                    graph = message["graph"]
                    print(
                        f"GRE Quants, Warning: message received for generate_questionGraph: received 'graph' instead of 'graph/table'.\n")
                return graph
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for questionGraph is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_parentTitle(self):
        def _generate(warn=False):
            prompt = f"ParentTitle"
            response = self.___getResponse(prompt, warn)

            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                return message["title"]
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for parentChildQuestion(generate_parentTitle) is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_childQuestionTitle(self, index):
        def _generate(warn=False):
            prompt = f"ChildQuestionTitle: {index}"
            response = self.___getResponse(prompt, warn)

            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                return message["title"]
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for parentChildQuestion(generate_childQuestionTitle) is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_childQuestion(self, index, child_prompt=""):
        def _generate(warn=False):
            prompt = f"generate ChildQuestion: {index} of {child_prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                return message["question"]
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for parentChildQuestion(generate_childQuestion) is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_childQuestion(self, index, child_prompt=""):
        def _generate(warn=False):
            prompt = f"generate ChildQuestion: {index} of {child_prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                return message["question"]
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for parentChildQuestion(generate_childQuestion) is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_childOptions(self, index):
        def _generate(warn=False):
            prompt = f"ChildOptions: {index}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                return message["options"], message["answer"]
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for parentChildQuestion(generate_childOptions) is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_childSolution(self, index):
        def _generate(warn=False):
            prompt = f"mode:- childQuestionSolution; question: {index}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                return message["solution"]
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for parentChildQuestion(generate_childSolution) is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result


class SimpleQuestion:
    def __init__(self, llm, system_instructions, global_state, prompt, lock):
        self.global_state = global_state
        self.lock = lock
        self.llm = llm
        self.prompt = prompt
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
            # Use 9 instead of 10 for safety margin
            if self.global_state["request_count"] >= 9:
                wait_time = 60 - elapsed + 1  # Add 1 second buffer
                if wait_time > 0:
                    print(
                        f"Rate limit safety: waiting {wait_time:.1f}s (requests: {self.global_state['request_count']}, elapsed: {elapsed:.1f}s)")
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
        for attempt in range(max_retries):
            try:
                result = func(*args, warn=True if attempt else False)
                if result:
                    return result
                print(
                    f"Retrying {func.__name__} - attempt {attempt + 1}/ {max_retries}")
            except Exception as e:
                last_error = str(e)
                print(f"Error in attempt {attempt + 1}: {last_error}")

        if last_error:
            print(f"All attempts failed. Last error: {last_error}")
            return None

    def generate_questionText(self):
        def _generate(warn=False):
            prompt = f"QuestionText: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                return message["question"]
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for questionText is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionTitle(self):
        def _generate(warn=False):
            prompt = f"QuestionTitle"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                return message["title"]
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for questionTitle is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionSolution(self, isNE=False):
        def _generate(warn=False):
            prompt = f"QuestionSolution"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                if isNE:
                    return message["solution"], float(message["answer"])
                else:
                    return message["solution"]
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for questionSolution is: \n{response}\nError: {str(e)}\n\n")
                return None
        if isNE:
            result = self._retry_generate(_generate)
            if result is None:
                return None, None
            result_solution, result_answer = result
            return result_solution, result_answer
        else:
            result = self._retry_generate(_generate)
            return result

    def generate_questionOptions(self):
        def _generate(warn=False):
            prompt = f"QuestionOptions"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                return message["options"], message["answer"]
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for questionOptions is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result


class DataSufficiencyQuestion:
    def __init__(self, llm, system_instructions, global_state, prompt, lock):
        self.global_state = global_state
        self.lock = lock
        self.llm = llm
        self.startTime = time.time()
        self.requestCounts = 0
        self.prompt = prompt
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
            # Use 9 instead of 10 for safety margin
            if self.global_state["request_count"] >= 9:
                wait_time = 60 - elapsed + 1  # Add 1 second buffer
                if wait_time > 0:
                    print(
                        f"Rate limit safety: waiting {wait_time:.1f}s (requests: {self.global_state['request_count']}, elapsed: {elapsed:.1f}s)")
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
        for attempt in range(max_retries):
            try:
                result = func(*args, warn=True if attempt else False)
                if result:
                    return result
                print(
                    f"Retrying {func.__name__} - attempt {attempt + 1}/ {max_retries}")
            except Exception as e:
                last_error = str(e)
                print(f"Error in attempt {attempt + 1}: {last_error}")

    def generate_questionText(self):
        def _generate(warn=False):
            prompt = f"QuestionText: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                return message["passage"], message["statements"], message["question"]
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for questionText is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        if result is None:
            return None, None, None
        result_passage, result_statements, result_question = result
        return result_passage, result_statements, result_question

    def generate_questionTitle(self):
        def _generate(warn=False):
            prompt = f"QuestionTitle"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                return message["title"]
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for questionTitle is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionSolution(self):
        def _generate(warn=False):
            prompt = f"QuestionSolution"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                return message["solution"], str(message["answer"])
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for questionSolution is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionOptions(self):
        def _generate(warn=False):
            prompt = f"QuestionOptions"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                

                # Check if this is an error response from refine_response

                if is_error_response(message):

                    print(f"Error: JSON parsing failed: {message.get('error', 'Unknown error')}")

                    return None
                return message["options"], message["answer"]
            except Exception as e:
                print(
                    f"GRE Quants, Error: message received for questionOptions is: \n{response}\nError: {str(e)}\n\n")
                return None
        result = self._retry_generate(_generate)
        return result
