import json
import re
import os
import time
from google import genai
from google.genai import types


def refine_response(response_text):
    """
    refines json responses, wrapped in json```{block}``` and  properly handles with new line inside the values and keys.
    """
    if not response_text or response_text.strip() == "":
        print("Warning: Empty response received")
        return '{"error": "Empty response received"}'

    def clean_json_string(text, response_text):
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
            print(
                f"Failed because we received this cleaned_text: \n{cleaned_text}\nAnd this was the json error message: \n{e}")
            print(f"this was the original text: \n{response_text}\n")
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
    markdown_match = re.search(
        r"```json\s*\n(.*?)\n\s*```", response_text, re.DOTALL)
    if markdown_match:
        try:
            group_text = markdown_match.group(1)
            if group_text and group_text.strip():
                new_text = group_text.strip()
        except (IndexError, AttributeError):
            pass

    # Pattern 2: ```\n{...}\n```
    if not new_text:
        json_block_match = re.search(
            r"```\s*\n(\{.*?\})\n\s*```", response_text, re.DOTALL)
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
    new_text = clean_json_string(new_text, response_text)

    if new_text is None:
        return '{"error": "Failed to parse JSON response: becuase clean_json_string received incomplete JSON text"}'

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
                    print(
                        f"  {key}: {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
            else:
                print(f"Parsed JSON is not a dict, it's: {type(parsed)}")
                print(
                    f"Content: {str(parsed)[:500]}{'...' if len(str(parsed)) > 500 else ''}")
        except Exception as parse_error:
            print(f"FAILED TO PARSE REFINED JSON: {str(parse_error)}")
    except Exception as refine_error:
        print(f"FAILED TO REFINE RESPONSE: {str(refine_error)}")

    print("=" * 80)
    print()


class GI:
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
            ))

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
            prompt = f"Mode: QuestionGraph\nPrompt: {self.prompt}\nreturn: `graph`"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message
            except Exception as e:
                print(
                    f"GMAT GI, Error: message received for questionGraph is:\n{response}\n Error: {str(e)}")
                return None
        result_graph = self._retry_generate(_generate)
        return result_graph

    def generate_questionText(self):
        def _generate(warn=False):
            prompt = "Mode: QuestionText return: `question`"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["question"]
            except Exception as e:
                print(
                    f"GMAT GI, Error: message received for questionText is: \n {response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionTitle(self):
        def _generate(warn=False):
            prompt = "Mode: QuestionTitle return: `title`"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(
                    f"GMAT GI, Error: message received for questionTitle is: {response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionSolution(self):
        def _generate(warn=False):
            prompt = "Mode: QuestionSolution return: `solution`"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                # Check if this is an error response from refine_response
                if is_error_response(message):
                    log_detailed_error("GMAT GI questionSolution - JSON parsing failed", response,
                                       f"refine_response returned error: {message.get('error', 'Unknown error')}",
                                       expected_keys=["solution", "answer", "explanation", "question"])
                    return None

                # Try different possible keys for solution data
                if "solution" in message:
                    return message["solution"]
                elif "answer" in message:
                    return message["answer"]
                elif "explanation" in message:
                    return message["explanation"]
                elif "question" in message:
                    return message["question"]
                else:
                    log_detailed_error("GMAT GI questionSolution - Missing expected keys", response,
                                       f"Expected solution keys not found. Available keys: {list(message.keys())}",
                                       expected_keys=["solution", "answer", "explanation", "question"])
                    return None
            except Exception as e:
                log_detailed_error("GMAT GI questionSolution - Exception during parsing", response, str(e),
                                   expected_keys=["solution", "answer", "explanation", "question"])
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_questionOptions(self):
        def _generate(warn=False):
            prompt = "Mode: QuestionOptions return: `options`, `answer`"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                # Try different possible keys for options and answers
                options = None
                answers = None

                # Look for options
                if "options" in message:
                    options = message["options"]
                elif "choices" in message:
                    options = message["choices"]
                elif "solution" in message:
                    # Sometimes solution contains the answer structure
                    options = message["solution"]

                # Look for answers
                if "answer" in message:
                    answers = message["answer"]
                elif "answers" in message:
                    answers = message["answers"]
                elif "solution" in message and options != message["solution"]:
                    answers = message["solution"]

                if options is not None and answers is not None:
                    return options, answers
                else:
                    print(
                        f"GMAT GI, Error: Expected 'options' and 'answer' keys not found in response: {list(message.keys())}")
                    return None
            except Exception as e:
                print(
                    f"GMAT GI, Error: message received for questionOptions is: {response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        if result is None:
            return None, None
        result_options, result_answer = result
        return result_options, result_answer


class MSR:
    def __init__(self, llm, system_instructions, global_state, prompt, lock):
        self.lock = lock
        self.global_state = global_state
        self.llm = llm
        self.prompt = prompt
        self.temp_prompt = None
        self.chat = self.llm.chats.create(
            model=os.getenv("MODEL"),
            config=types.GenerateContentConfig(
                system_instruction=system_instructions
            ))

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
                print(
                    f"Error in attempt {attempt + 1}: {last_error}\n\ngot result value: {result}")

        if last_error:
            print(f"All attempts failed. Last error: {last_error}")
            return None

    def generate_SourceInfo(self, prompt):
        self.temp_prompt = prompt

        def _generate(warn=False):
            response = self.___getResponse(self.temp_prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message
            except Exception as e:
                print(
                    f"GMAT MSR, Error received for SourceInfo is: \n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_MainQuestionTitle(self):
        def _generate(warn=False):
            prompt = "MainQuestionTitle (based on the the given question data what wuold be a unique question title of complete Multi Source Reasoning question)"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(
                    f"GMAT MSR, Error: message received for MainQuestionTitle is:\n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionText(self, prompt):
        self.temp_prompt = prompt

        def _generate(warn=False):
            response = self.___getResponse(self.temp_prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["question"]
            except Exception as e:
                print(
                    f"GMAT MSR, Error: message received for QuestionText generation is:\n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionTitle(self, prompt):
        self.temp_prompt = prompt

        def _generate(warn=False):
            response = self.___getResponse(self.temp_prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(
                    f"GMAT MSR, Error: message received for QuestionTitle generation is:\n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionSolution(self, prompt):
        self.temp_prompt = prompt

        def _generate(warn=False):
            response = self.___getResponse(self.temp_prompt, warn)
            print(
                f"XXXXXX\nThis is what we got in solution:\n\n{response}\n\n=============================")
            try:
                message = json.loads(refine_response(response))
                return message["solution"]
            except Exception as e:
                print(
                    f"GMAT MSR, Error: message received for QuestionSolution generation is:\n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionOptions(self, prompt, question_style):
        self.temp_prompt = [prompt, question_style]

        def _generate(warn=False):
            prompt = self.temp_prompt[0]
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                question_style = self.temp_prompt[1]
                if question_style == "MCQ (5 options MCQ)":
                    return message["options"], message["answer"]
                else:
                    return message["options"]
            except Exception as e:
                print(
                    f"GMAT MSR, Error: message received for QuestionOptions is: \n{response}\nError: {str(e)}")
                return None
        if question_style == "MCQ (5 options MCQ)":
            result = self._retry_generate(_generate)
            if result is None:
                return None, None
            result_options, result_answer = result
            return result_options, result_answer
        result = self._retry_generate(_generate)
        return result


class TA:
    def __init__(self, llm, system_instructions, global_state, prompt, lock):
        self.global_state = global_state
        self.lock = lock
        self.llm = llm
        self.prompt = prompt

        self.temp_data = None
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

    def generate_QuestionTable(self, no_rows, no_cols):
        self.temp_data = [no_rows, no_cols]

        def _generate(warn=False):
            no_rows = self.temp_data[0]
            no_cols = self.temp_data[1]
            prompt = f"QuestionTable, no_rows: {no_rows}, no_cols: {no_cols}; InputPrompt: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                # Check if this is an error response from refine_response
                if is_error_response(message):
                    log_detailed_error("GMAT TA QuestionTable - JSON parsing failed", response,
                                       f"refine_response returned error: {message.get('error', 'Unknown error')}",
                                       expected_keys=["tables", "content", "table"])
                    return None

                # Try different possible keys for table data
                if "tables" in message:
                    return message["tables"]
                elif "content" in message:
                    return message["content"]
                elif "table" in message:
                    return message["table"]
                else:
                    log_detailed_error("GMAT TA QuestionTable - Missing expected keys", response,
                                       f"Expected keys not found. Available keys: {list(message.keys())}",
                                       expected_keys=["tables", "content", "table"])
                    return None
            except Exception as e:
                log_detailed_error("GMAT TA QuestionTable - Exception during parsing", response, str(e),
                                   expected_keys=["tables", "content", "table"])
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionText(self):
        def _generate(warn=False):
            prompt = f"QuestionText"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                # Try different possible keys for question text
                if "question" in message:
                    return message["question"]
                elif "text" in message:
                    return message["text"]
                elif "content" in message:
                    return message["content"]
                elif "title" in message:
                    return message["title"]
                else:
                    print(
                        f"GMAT TA, Error: Expected 'question', 'text', 'content', or 'title' key not found in response: {list(message.keys())}")
                    return None
            except Exception as e:
                print(
                    f"GMAT TA, Error: message received for QuestionText is: \n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionTitle(self):
        def _generate(warn=False):
            prompt = "QuestionTitle"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(
                    f"GMAT TA, Error: message received for QuestionTitle is: \n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result

    def generate_QuestionOptions(self):
        def _generate(warn=False):
            prompt = f"QuestionOptions"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                # Check if this is an error response from refine_response
                if is_error_response(message):
                    log_detailed_error("GMAT TA QuestionOptions - JSON parsing failed", response,
                                       f"refine_response returned error: {message.get('error', 'Unknown error')}",
                                       expected_keys=["options", "answer", "choices", "answers"])
                    return None

                # Try different possible keys for options and answers
                options = None
                answers = None

                # Look for options
                if "options" in message:
                    options = message["options"]
                elif "choices" in message:
                    options = message["choices"]
                elif "question" in message:
                    options = message["question"]

                # Look for answers
                if "answer" in message:
                    answers = message["answer"]
                elif "answers" in message:
                    answers = message["answers"]
                elif "solution" in message:
                    answers = message["solution"]

                if options is not None and answers is not None:
                    return options, answers
                else:
                    log_detailed_error("GMAT TA QuestionOptions - Missing expected keys", response,
                                       f"Could not find both options and answers. Available keys: {list(message.keys())}. "
                                       f"Options found: {options is not None}, Answers found: {answers is not None}",
                                       expected_keys=["options", "answer", "choices", "answers"])
                    return None
            except Exception as e:
                log_detailed_error("GMAT TA QuestionOptions - Exception during parsing", response, str(e),
                                   expected_keys=["options", "answer", "choices", "answers"])
                return None
        result = self._retry_generate(_generate)
        if result is None:
            return None, None
        result_options, result_answer = result
        return result_options, result_answer

    def generate_QuestionSolution(self):
        def _generate(warn=False):
            prompt = "QuestionSolution"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["solution"]
            except Exception as e:
                print(
                    f"GMAT TA, Error: message received for QuestionSolution is: \n{response}\nError: {str(e)}")
                return None
        result = self._retry_generate(_generate)
        return result


class TPA:
    def __init__(self, llm, system_instruction, global_state, prompt, lock):
        self.lock = lock
        self.global_state = global_state
        self.llm = llm
        self.prompt = prompt
        self.max_retries = 3
        self.startTime = time.time()
        self.requestCounts = 0
        self.chat = self.llm.chats.create(
            model=os.getenv("MODEL"),
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
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

    def generate_ParentQuestionContent(self):
        def _generate(warn=False):
            prompt = f"ParentQuestionContent: {self.prompt}"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))

                # Check if this is an error response from refine_response
                if is_error_response(message):
                    log_detailed_error("GMAT TPA ParentQuestionContent - JSON parsing failed", response,
                                       f"refine_response returned error: {message.get('error', 'Unknown error')}",
                                       expected_keys=["content", "question", "graph", "data"])
                    return None

                # Try different possible keys for content data
                if "content" in message:
                    return message["content"]
                elif "question" in message:
                    return message["question"]
                elif "graph" in message:
                    return message["graph"]
                elif "data" in message:
                    return message["data"]
                else:
                    log_detailed_error("GMAT TPA ParentQuestionContent - Missing expected keys", response,
                                       f"Expected content keys not found. Available keys: {list(message.keys())}",
                                       expected_keys=["content", "question", "graph", "data"])
                    return None
            except Exception as e:
                log_detailed_error("GMAT TPA ParentQuestionContent - Exception during parsing", response, str(e),
                                   expected_keys=["content", "question", "graph", "data"])
                return None

        result = self._retry_generate(_generate)
        return result

    def generate_QuestionText(self, difficulties):
        def _generate(warn=False):
            questions = []
            for i in range(1, 3):
                prompt = f"Question{i}: difficulty Level:{difficulties[i-1]} "
                response = self.___getResponse(prompt, warn)
                try:
                    message = json.loads(refine_response(response))
                    questions.append(message["question"])
                except Exception as e:
                    print(
                        f"GMAT TPA, Error message: received for QuestionText:\n{response}\nError: {str(e)}")
                    return None
            return questions

        result = self._retry_generate(_generate)
        return result if result else []

    def generate_QuestionTitle(self):
        def _generate(warn=False):
            prompt = "QuestionTitle"
            response = self.___getResponse(prompt, warn)
            try:
                message = json.loads(refine_response(response))
                return message["title"]
            except Exception as e:
                print(
                    f"GMAT TPA, Error received in QuestionTitle: {response}\nError: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result

    def generate_QuestionSolution(self):
        def _generate(warn=False):
            solutions = []
            for i in range(1, 3):
                prompt = f"QuestionSolution {i}"
                response = self.___getResponse(prompt, warn)
                try:
                    message = json.loads(refine_response(response))
                    solutions.append(message["solution"])
                except Exception as e:
                    print(
                        f"GMAT TPA, Error: message received for QuestionSolution is: \n{response}\nError: {str(e)}\n\n")
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
                print(
                    f"GMAT TPA,didn't get proper options and answers, here is how the complete message looks like:\n{message}")
                return None
            except Exception as e:
                print(
                    f"GMAT TPA, Error: message received for QuestionOptions is: \n{response}\nError:{str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result
