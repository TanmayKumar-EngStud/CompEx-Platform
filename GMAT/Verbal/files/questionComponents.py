import json, re

def refine_response(response_text):
    try:
        # First try to parse as JSON directly
        json.loads(response_text)
        return response_text
    except json.JSONDecodeError:
        try:
            # Look for JSON-like structure between curly braces
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_string = json_match.group(0)
            else:
                return None

            # Clean up the extracted JSON string
            json_string = re.sub(r'\s+', ' ', json_string.strip())
            
            # Step 1: Handle LaTeX-style expressions by replacing backslashes with placeholders
            placeholders = {
                '\\text': '{{TEXT}}',
                '\\left': '{{LEFT}}',
                '\\right': '{{RIGHT}}',
                '\\(': '{{LATEX_START}}',
                '\\)': '{{LATEX_END}}',
                '\\$': '{{DOLLAR}}',
                '\\%': '{{PERCENT}}'
            }
            for key, value in placeholders.items():
                json_string = json_string.replace(key, value)
            
            # Step 2: Handle quotes
            # Replace escaped double quotes first
            json_string = json_string.replace('\\"', '{{ESCAPED_QUOTE}}')
            # Replace single quotes with double quotes
            json_string = re.sub(r"(?<!\\)'", '"', json_string)
            # Replace key-value single quotes patterns
            json_string = re.sub(r":\s*'", ': "', json_string)
            json_string = re.sub(r"'\s*,", '",', json_string)
            json_string = re.sub(r"'\s*}", '"}', json_string)
            json_string = re.sub(r"'\s*]", '"]', json_string)
            
            # Step 3: Restore all placeholders
            reverse_placeholders = {v: k for k, v in placeholders.items()}
            reverse_placeholders['{{ESCAPED_QUOTE}}'] = '\\"'
            for key, value in reverse_placeholders.items():
                json_string = json_string.replace(key, value)
            
            # Clean up trailing commas
            json_string = re.sub(r',\s*}', '}', json_string)
            json_string = re.sub(r',\s*]', ']', json_string)

            # Final validation
            parsed_json = json.loads(json_string)
            return json_string
        except json.JSONDecodeError as je:
            print(f"JSON validation failed: {str(je)}")
            print(f"Position: {je.pos}")
            print(f"Line: {je.lineno}, Column: {je.colno}")
            print(f"Document: {json_string[max(0, je.pos-50):min(len(json_string), je.pos+50)]}")
            return None
        except Exception as e:
            print(f"Processing failed: {str(e)}")
            print(f"Problematic text: {response_text[:200]}...")
            return None
class ParentChildQuestion:
    def __init__(self, llm, prompt, thread_id=None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id
    def generate_parentPassage(self):
        response = self.llm.invoke({"content":f"ParentQuestion: {self.prompt}"})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            self.thread_id = response[0].thread_id if response else "GMAT Verbal, Error! thread_id not found! (questionComponent@l:115)"
            return self.thread_id, message["passages"]
        except Exception as e:
            print(f"GMAT Verbal, Error: message received for parentPassage is: \n{response[0].content[0].text.value}\n\n")
            return "", ""
    
    def generate_parentTitle(self):
        response = self.llm.invoke({"content": f"ParentTitle", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            print(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_parentTitle) is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_childQuestionTitle(self, index):
        response = self.llm.invoke({"content": f"ChildQuestionTitle: {index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            print(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_childQuestionTitle) is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_childQuestion(self, index, child_prompt=""):
        response = self.llm.invoke({"content": f"ChildQuestion: {index} of {child_prompt}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["question"]
        except Exception as e:
            print(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_childQuestion) is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_childOptions(self, index):
        response = self.llm.invoke({"content": f"ChildOptions: {index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["options"], message["answer"]
        except Exception as e:
            print(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_childOptions) is: \n{response[0].content[0].text.value}\n\n")
            return {}, ""
    def generate_childSolution(self, index):
        response = self.llm.invoke({"content": f"ChildSolution: {index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["solution"]
        except Exception as e:
            print(f"GMAT Verbal, Error: message received for parentChildQuestion(generate_childSolution) is: \n{response[0].content[0].text.value}\n\n")
            return ""

class SimpleQuestion:
    def __init__(self, llm, prompt, thread_id= None):
        self.llm = llm
        self.thread_id = thread_id
        self.prompt = prompt
    def generate_questionText(self):
        response = self.llm.invoke({"content":f"QuestionText: {self.prompt}"})
        try:
            response_text = refine_response([message.content[0].text.value for message in response][0])
            message = json.loads(response_text)
            self.thread_id = response[0].thread_id if response else "GMAT Verbal, Error! thread_id not found! (questionComponent@l:30)"
            if("sentence correction" in self.prompt.lower()):
                return self.thread_id, message["question"]
            else:
                return self.thread_id, message["passage"], message["question"]
        except Exception as e:
            print(f"GMAT Verbal, Error: message received for questionText is: \n{[message.content[0].text.value for message in response][0]}\n\n")
            print(f"Exception details: {str(e)}")
            return "", ""
    def generate_questionTitle(self):
        response = self.llm.invoke({"content":f"QuestionTitle", "thread_id": self.thread_id})
        try:
            response_text = refine_response([message.content[0].text.value for message in response][0])
            message = json.loads(response_text)
            return message["title"]
        except Exception as e:
            # message received is:
            print(f"GMAT Verbal, Error: message received for questionTitle is: \n{[message.content[0].text.value for message in response][0]}\n\n")
            return ""
    def generate_questionSolution(self):
        response = self.llm.invoke({"content":f"QuestionSolution", "thread_id": self.thread_id})
        try:
            response_text = refine_response([message.content[0].text.value for message in response][0])
            if isinstance(response_text, dict):
                message = response_text
            else:
                message = json.loads(response_text)    
            return message["solution"]
        except Exception as e:
            print(f"GMAT Verbal, Error: message received for questionSolution is: \n{response[0].content[0].text.value}\n\n")
            print(f"JSON parsing error: {str(e)}")
            return "", ""
    def generate_questionOptions(self):
      response = self.llm.invoke({"content":f"QuestionOptions", "thread_id": self.thread_id})
      try:
         raw_response = response[0].content[0].text.value
         json_string = refine_response(raw_response.replace("'", '"'))
         message = json.loads(json_string)
         return message["options"], message["answer"]
      except Exception as e:
         print(f"GMAT Verbal, Error: message received for questionOptions is: \n{response[0].content[0].text.value}\n\n")
         print(f"JSON parsing error: {str(e)}")
         return {}, ""

