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
                # Handle single quotes
                json_str = json_str.replace("'", '"')
                # Remove trailing commas
                json_str = re.sub(r',(\s*})', r'\1', json_str)
                json_str = re.sub(r',(\s*])', r'\1', json_str)
                
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

class ParentChildQuestion:
    def __init__(self, llm, prompt, thread_id=None):
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

    def generate_passages(self):
        def _generate():
            if self.thread_id:
                response = self.llm.invoke({"content": f"ParentQuestion: {self.prompt}", "thread_id": self.thread_id})
            else:
                response = self.llm.invoke({"content": f"ParentQuestion: {self.prompt}"})
                self.thread_id = response[0].thread_id if response else None
            
            try:
                message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
                return message.get("passages", [])
            except Exception as e:
                print(f"GRE Verbal, Error in generate_passages: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result if result else []

    def generate_parentTitle(self):
        def _generate():
            response = self.llm.invoke({"content": f"ParentTitle", "thread_id": self.thread_id})
            try:
                message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
                return message.get("title", "")
            except Exception as e:
                print(f"GRE Verbal, Error in generate_parentTitle: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result if result else ""

    def generate_childQuestion(self, index, child_prompt=""):
        def _generate():
            response = self.llm.invoke({"content": f"ChildQuestion: {index} of {child_prompt}", "thread_id": self.thread_id})
            try:
                message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
                return message.get("question", "")
            except Exception as e:
                print(f"GRE Verbal, Error in generate_childQuestion: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result if result else ""

    def generate_childQuestionTitle(self, index):
        def _generate():
            response = self.llm.invoke({"content": f"ChildTitle: {index}", "thread_id": self.thread_id})
            try:
                message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
                return message.get("title", "")
            except Exception as e:
                print(f"GRE Verbal, Error in generate_childQuestionTitle: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result if result else ""

    def generate_childOptions(self, index):
        def _generate():
            response = self.llm.invoke({"content": f"ChildOptions: {index}", "thread_id": self.thread_id})
            try:
                message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
                if message.get("options") and message.get("answer"):
                    return message["options"], message["answer"]
                return None
            except Exception as e:
                print(f"GRE Verbal, Error in generate_childOptions: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result if result else ([], "")

    def generate_childSolution(self, index):
        def _generate():
            response = self.llm.invoke({"content": f"ChildSolution: {index}", "thread_id": self.thread_id})
            try:
                message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
                return message.get("solution", "")
            except Exception as e:
                print(f"GRE Verbal, Error in generate_childSolution: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result if result else ""

class SimpleQuestion:
    def __init__(self, llm, prompt, thread_id=None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id
        self.max_retries = 3

    def _retry_generate(self, func, *args):
        last_error = None
        func_name = func.__name__
        for attempt in range(self.max_retries):
            try:
                result = func(*args)
                if result:  # If we got any non-None result, return it
                    return result
                print(f"⚠️  GRE Verbal {func_name} - attempt {attempt + 1}/{self.max_retries} failed")
                print("   Reason: Function returned None")
            except Exception as e:
                last_error = str(e)
                print(f"⚠️  GRE Verbal {func_name} - attempt {attempt + 1}/{self.max_retries} failed")
                print(f"   Error: {last_error}")
        
        # If we get here, all attempts failed
        if last_error:
            print(f"❌ GRE Verbal {func_name}: Failed after {self.max_retries} attempts")
            print(f"   Last Error: {last_error}")
        else:
            print(f"❌ GRE Verbal {func_name}: Failed after {self.max_retries} attempts")
            print("   Reason: All attempts returned None")
        return None

    def generate_questionText(self):
        def _generate():
            try:
                if self.thread_id:
                    response = self.llm.invoke({"content": f"QuestionText: {self.prompt}", "thread_id": self.thread_id})
                else:
                    response = self.llm.invoke({"content": f"QuestionText: {self.prompt}"})
                    if not response:
                        raise Exception("No response received from LLM")
                    self.thread_id = response[0].thread_id if response else None
                    if not self.thread_id:
                        raise Exception("Failed to get thread_id from response")

                raw_response = [message.content[0].text.value for message in response][0]

                # First try to parse it directly as JSON
                try:
                    message = json.loads(raw_response)
                except json.JSONDecodeError as je:
                    # If direct parsing fails, try refine_response
                    print(f"Direct JSON parsing failed: {str(je)}")
                    print("Trying refine_response...")
                    refined_response = refine_response(raw_response)
                    if not refined_response:
                        raise Exception("Failed to refine response - refine_response returned None")
                    
                    print(f"\nRefined Response:\n{refined_response}\n")
                    try:
                        message = json.loads(refined_response)
                    except json.JSONDecodeError as je2:
                        raise Exception(f"Failed to parse refined response: {str(je2)}")

                if "CR" in self.prompt:
                    if not message.get("passage"):
                        raise Exception("Missing 'passage' field in response")
                    if not message.get("question"):
                        raise Exception("Missing 'question' field in response")
                    return self.thread_id, message["passage"], message["question"]
                else:
                    if not message.get("question"):
                        raise Exception("Missing 'question' field in response")
                    return self.thread_id, message["question"]

            except Exception as e:
                print(f"GRE Verbal Error in generate_questionText:")
                print(f"  Error Type: {type(e).__name__}")
                print(f"  Error Message: {str(e)}")
                if 'response' in locals():
                    try:
                        print(f"Raw response content:\n{[m.content[0].text.value for m in response][0]}\n")
                    except:
                        print("Could not extract raw response content")
                return None

        result = self._retry_generate(_generate)
        if not result:
            return ("", "") if "CR" not in self.prompt else ("", "", "")
        return result

    def generate_questionTitle(self):
        def _generate():
            try:
                if not self.thread_id:
                    raise Exception("No thread_id available - question text generation may have failed")
                
                response = self.llm.invoke({"content": "QuestionTitle", "thread_id": self.thread_id})
                if not response:
                    raise Exception("No response received from LLM")

                raw_response = [message.content[0].text.value for message in response][0]

                # First try to parse it directly as JSON
                try:
                    message = json.loads(raw_response)
                except json.JSONDecodeError as je:
                    # If direct parsing fails, try refine_response
                    print(f"Direct JSON parsing failed: {str(je)}")
                    print("Trying refine_response...")
                    refined_response = refine_response(raw_response)
                    if not refined_response:
                        raise Exception("Failed to refine title response - refine_response returned None")
                    
                    
                    try:
                        message = json.loads(refined_response)
                    except json.JSONDecodeError as je2:
                        raise Exception(f"Failed to parse refined title response: {str(je2)}")

                if not message.get("title"):
                    raise Exception("Missing 'title' field in response")
                return message["title"]

            except Exception as e:
                print(f"GRE Verbal Error in generate_questionTitle:")
                print(f"  Error Type: {type(e).__name__}")
                print(f"  Error Message: {str(e)}")
                return None

        result = self._retry_generate(_generate)
        return result if result else ""

    def generate_questionSolution(self):
        def _generate():
            try:
                if not self.thread_id:
                    raise Exception("No thread_id available - question text generation may have failed")
                
                response = self.llm.invoke({"content": "QuestionSolution", "thread_id": self.thread_id})
                if not response:
                    raise Exception("No response received from LLM")

                raw_response = [message.content[0].text.value for message in response][0]
                

                # First try to parse it directly as JSON
                try:
                    message = json.loads(raw_response)
                except json.JSONDecodeError as je:
                    # If direct parsing fails, try refine_response
                    print(f"Direct JSON parsing failed: {str(je)}")
                    print("Trying refine_response...")
                    refined_response = refine_response(raw_response)
                    if not refined_response:
                        raise Exception("Failed to refine solution response - refine_response returned None")
                    
                    print(f"\nRefined Solution Response:\n{refined_response}\n")
                    try:
                        message = json.loads(refined_response)
                    except json.JSONDecodeError as je2:
                        raise Exception(f"Failed to parse refined solution response: {str(je2)}")

                if not message.get("solution"):
                    raise Exception("Missing 'solution' field in response")
                return message["solution"]

            except Exception as e:
                print(f"GRE Verbal Error in generate_questionSolution:")
                print(f"  Error Type: {type(e).__name__}")
                print(f"  Error Message: {str(e)}")
                if 'response' in locals():
                    try:
                        print(f"Raw solution response content:\n{[m.content[0].text.value for m in response][0]}\n")
                    except:
                        print("Could not extract raw solution response content")
                return None

        result = self._retry_generate(_generate)
        return result if result else ""

    def generate_questionOptions(self, num_options):
        def _generate():
            try:
                if not self.thread_id:
                    raise Exception("No thread_id available - question text generation may have failed")
                
                response = self.llm.invoke({"content": f"QuestionOptions, number of options: {num_options}", "thread_id": self.thread_id})
                if not response:
                    raise Exception("No response received from LLM")

                raw_response = [message.content[0].text.value for message in response][0]


                # First try to parse it directly as JSON
                try:
                    message = json.loads(raw_response)

                except json.JSONDecodeError as je:
                    # If direct parsing fails, try refine_response
                    print(f"Direct JSON parsing failed: {str(je)}")
                    print("Trying refine_response...")
                    refined_response = refine_response(raw_response)
                    if not refined_response:
                        raise Exception("Failed to refine options response - refine_response returned None")
                    
                    print(f"\nRefined Options Response:\n{refined_response}\n")
                    try:
                        message = json.loads(refined_response)
                    except json.JSONDecodeError as je2:
                        raise Exception(f"Failed to parse refined options response: {str(je2)}")

                if not message.get("options"):
                    raise Exception("Missing 'options' field in response")
                if not message.get("answer"):
                    raise Exception("Missing 'answer' field in response")
                return message["options"], message["answer"]

            except Exception as e:
                print(f"GRE Verbal Error in generate_questionOptions:")
                print(f"  Error Type: {type(e).__name__}")
                print(f"  Error Message: {str(e)}")
                if 'response' in locals():
                    try:
                        print(f"Raw options response content:\n{[m.content[0].text.value for m in response][0]}\n")
                    except:
                        print("Could not extract raw options response content")
                return None

        result = self._retry_generate(_generate)
        return result if result else ([], "")