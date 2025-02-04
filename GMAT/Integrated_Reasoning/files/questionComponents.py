import json, re

def refine_response(response_text):
    """
    A simplified function to handle JSON responses, including those wrapped in ```json code blocks.
    """
    if not response_text:
        return None
        
    try:
        # First try to parse as pure JSON
        try:
            json.loads(response_text)
            return response_text  # If it's valid JSON, return as is
        except json.JSONDecodeError:
            pass

        # Look for ```json blocks
        json_block_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_block_match:
            try:
                json_str = json_block_match.group(1).strip()

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
                
                parsed = json.loads(json_str)
                return json.dumps(parsed)
            except json.JSONDecodeError as e:
                print(f"JSON validation error in code block: {str(e)}\nJSON string:\n{json_str}\n")
                # Continue to try other methods
        
        # Clean up the text a bit
        text = response_text.strip()
        
        # If it starts with { and ends with }, try to parse it
        if text.startswith('{') and text.endswith('}'):
            try:
                # Handle single quotes
                text = text.replace("'", '"')
                # Remove trailing commas before } or ]
                text = re.sub(r',(\s*})', r'\1', text)
                text = re.sub(r',(\s*])', r'\1', text)
                
                # Try to parse again
                parsed = json.loads(text)
                return json.dumps(parsed)
            except json.JSONDecodeError as e:
                print(f"JSON validation error: {str(e)}\nJSON string:\n{text}\n")
                return None
        
        # If we get here, try to find JSON in the text
        match = re.search(r'(\{.*\})', text, re.DOTALL)
        if match:
            try:
                json_str = match.group(1)
                # Handle single quotes
                json_str = json_str.replace("'", '"')
                # Remove trailing commas
                json_str = re.sub(r',(\s*})', r'\1', json_str)
                json_str = re.sub(r',(\s*])', r'\1', json_str)
                
                parsed = json.loads(json_str)
                return json.dumps(parsed)
            except json.JSONDecodeError as e:
                print(f"JSON validation error: {str(e)}\nJSON string:\n{json_str}\n")
                return None
                
        return None
            
    except Exception as e:
        print(f"Error in refine_response: {str(e)}")
        return None

class GI: 
    def __init__(self, llm, prompt, thread_id= None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id
    def generate_questionGraph(self):
        if(self.thread_id):
            response = self.llm.invoke({"content":f"QuestionGraph: {self.prompt}", "thread_id": self.thread_id})
        else:
            response = self.llm.invoke({"content":f"QuestionGraph: {self.prompt}"})
            self.thread_id = response[0].thread_id if response else "GMAT IR, Error! thread_id not found for GI (questionComponent@l:131)"
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return self.thread_id, message["graphs"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for questionGraph is: \n{response[0].content[0].text.value}\n\n")
            return "", ""
    def generate_questionText(self):
        response = self.llm.invoke({"content":f"QuestionText", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["question"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for questionText is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_questionTitle(self):
        response = self.llm.invoke({"content":f"QuestionTitle", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for questionTitle is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_questionSolution(self):
        response = self.llm.invoke({"content":f"QuestionSolution", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["solution"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for questionSolution is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_questionOptions(self):
        response = self.llm.invoke({"content":f"QuestionOptions", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["options"], message["answer"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for questionOptions is: \n{response[0].content[0].text.value}\n\n")
            return [], ""

class MSR: 
    def __init__(self, llm, prompt, thread_id= None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id
    def generate_SourceInfo(self, prompt):
        if(self.thread_id):
            response = self.llm.invoke({"content":f"{prompt}", "thread_id": self.thread_id})
        else:
            response = self.llm.invoke({"content":f"{prompt}"})
            self.thread_id = response[0].thread_id if response else "GMAT IR, Error! thread_id not found for MSR (questionComponent@l:131)"
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return self.thread_id, message
        except Exception as e:
            print(f"GMAT IR, Error: message received for SourceInfo is: \n{response[0].content[0].text.value}\n\n")
            return "", ""
    def generate_MainQuestionTitle(self):
        response = self.llm.invoke({"content":f"MainQuestionTitle (based on the given question data what would be a unique question title of complete Multiple Source Reasoning question)", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for MainQuestionTitle is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionText(self, prompt):
        response = self.llm.invoke({"content":f"{prompt}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["question"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionText is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionTitle(self, prompt):
        response = self.llm.invoke({"content":f"{prompt}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionTitle is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionSolution(self, prompt):
        response = self.llm.invoke({"content":f"{prompt}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["solution"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionSolution is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionOptions(self, prompt, question_style):
        response = self.llm.invoke({"content":f"{prompt}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            if question_style == "MCQ (5 options MCQ)":
                return message["options"], message["answer"]
            else:
                return message["options"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionOptions is: \n{response[0].content[0].text.value}\n\n")
            return [], ""

class TA:
    def __init__(self, llm, prompt, thread_id= None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id
    def generate_QuestionTable(self):
        if(self.thread_id):
            response = self.llm.invoke({"content":f"QuestionTable", "thread_id": self.thread_id})
        else:
            response = self.llm.invoke({"content":f"QuestionTable: {self.prompt}"})
            self.thread_id = response[0].thread_id if response else "GMAT IR, Error! thread_id not found for TA (questionComponent@l:131)"
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return self.thread_id, message["tables"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionTable is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionText(self):
        response = self.llm.invoke({"content":f"QuestionText", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["question"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionText is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionTitle(self):
        response = self.llm.invoke({"content":f"QuestionTitle", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionTitle is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionOptions(self):
        response = self.llm.invoke({"content":f"QuestionOptions", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["options"], message["answer"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionOptions is: \n{response[0].content[0].text.value}\n\n")
            return [], {}
    def generate_QuestionSolution(self):
        response = self.llm.invoke({"content":f"QuestionSolution", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["solution"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionSolution is: \n{response[0].content[0].text.value}\n\n")
            return ""
    
class TPA:
    def __init__(self, llm, prompt, thread_id= None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id
        self.max_retries = 3

    def _retry_generate(self, func, *args):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                result = func(*args)
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

    def generate_QuestionText(self):
        def _generate():
            try:
                if(self.thread_id):
                    response = self.llm.invoke({"content":f"QuestionText: {self.prompt}", "thread_id": self.thread_id})
                else:
                    response = self.llm.invoke({"content":f"QuestionText: {self.prompt}"})
                    self.thread_id = response[0].thread_id if response else None
                
                # Get the raw response text
                raw_response = [message.content[0].text.value for message in response][0]
                # print(f"\nGMAT IR TPA Raw Response:\n{raw_response}\n")
                
                # First try to parse it directly as JSON
                try:
                    message = json.loads(raw_response)
                    # print("Successfully parsed raw response as JSON")
                except json.JSONDecodeError:
                    # If direct parsing fails, try refine_response
                    print("Direct JSON parsing failed, trying refine_response")
                    refined_response = refine_response(raw_response)
                    if not refined_response:
                        print("Failed to refine response")
                        return None
                        
                    print(f"\nRefined Response:\n{refined_response}\n")
                    message = json.loads(refined_response)
                
                # Ensure required fields exist with default values
                part1 = message.get("part1", {})
                if not isinstance(part1, dict):
                    part1 = {}
                part1.setdefault("description", "")
                part1.setdefault("graph", None)
                part1.setdefault("table", None)
                
                part2 = message.get("part2", {})
                if not isinstance(part2, dict):
                    part2 = {}
                part2.setdefault("description", "")
                part2.setdefault("graph", None)
                part2.setdefault("table", None)
                
                question = message.get("question", "")
                qtype = message.get("type", "two-part analysis")
                
                # Return all required values
                return self.thread_id, part1, part2, question, qtype
                    
            except Exception as e:
                print(f"Error in generate_QuestionText: {str(e)}")
                if 'response' in locals():
                    try:
                        print(f"Raw response content:\n{[m.content[0].text.value for m in response][0]}\n")
                    except:
                        print("Could not extract raw response content")
                return None

        result = self._retry_generate(_generate)
        if not result:
            # Return a default structure if all retries fail
            default_part = {"description": "", "graph": None, "table": None}
            return "", default_part, default_part, "", "two-part analysis"
        return result

    def generate_QuestionTitle(self):
        def _generate():
            response = self.llm.invoke({"content":f"QuestionTitle", "thread_id": self.thread_id})
            try:
                raw_response = [message.content[0].text.value for message in response][0]
                # First try direct JSON parsing
                try:
                    message = json.loads(raw_response)
                except json.JSONDecodeError:
                    # If that fails, try refine_response
                    refined_response = refine_response(raw_response)
                    if not refined_response:
                        return None
                    message = json.loads(refined_response)
                return message.get("title", "")
            except:
                return None

        result = self._retry_generate(_generate)
        return result if result else ""

    def generate_QuestionSolution(self):
        def _generate():
            response = self.llm.invoke({"content":f"QuestionSolution", "thread_id": self.thread_id})
            try:
                raw_response = [message.content[0].text.value for message in response][0]
                # First try direct JSON parsing
                try:
                    message = json.loads(raw_response)
                except json.JSONDecodeError:
                    # If that fails, try refine_response
                    refined_response = refine_response(raw_response)
                    if not refined_response:
                        return None
                    message = json.loads(refined_response)
                return message.get("solution", "")
            except:
                return None

        result = self._retry_generate(_generate)
        return result if result else ""

    def generate_QuestionOptions(self):
        def _generate():
            response = self.llm.invoke({"content":f"QuestionOptions", "thread_id": self.thread_id})
            try:
                raw_response = [message.content[0].text.value for message in response][0]
                # First try direct JSON parsing
                try:
                    message = json.loads(raw_response)
                except json.JSONDecodeError:
                    # If that fails, try refine_response
                    refined_response = refine_response(raw_response)
                    if not refined_response:
                        return None
                    message = json.loads(refined_response)
                if message.get("options") and message.get("answer"):
                    return message["options"], message["answer"]
                return None
            except:
                return None

        result = self._retry_generate(_generate)
        return result if result else ([], {})