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
    def generate_SourceInfo(self, source_index):
        if(self.thread_id):
            response = self.llm.invoke({"content":f"SourceInfo_{source_index}: {self.prompt}", "thread_id": self.thread_id})
        else:
            response = self.llm.invoke({"content":f"SourceInfo_{source_index}: {self.prompt}"})
            self.thread_id = response[0].thread_id if response else "GMAT IR, Error! thread_id not found for MSR (questionComponent@l:131)"
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return self.thread_id, message
        except Exception as e:
            print(f"GMAT IR, Error: message received for SourceInfo_{source_index} is: \n{response[0].content[0].text.value}\n\n")
            return "", ""
    def generate_MainQuestionTitle(self):
        response = self.llm.invoke({"content":f"MainQuestionTitle", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for MainQuestionTitle is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionText(self, question_index):
        response = self.llm.invoke({"content":f"QuestionText_{question_index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["question"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionText_{question_index} is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionTitle(self, question_index):
        response = self.llm.invoke({"content":f"QuestionTitle_{question_index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionTitle_{question_index} is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionSolution(self, question_index):
        response = self.llm.invoke({"content":f"QuestionSolution_{question_index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["solution"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionSolution_{question_index} is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionOptions(self, question_index):
        response = self.llm.invoke({"content":f"QuestionOptions_{question_index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["options"], message["answer"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionOptions_{question_index} is: \n{response[0].content[0].text.value}\n\n")
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
    def generate_QuestionText(self):
        if(self.thread_id):
            response = self.llm.invoke({"content":f"QuestionText: {self.prompt}", "thread_id": self.thread_id})
        else:
            response = self.llm.invoke({"content":f"QuestionText: {self.prompt}"})
            self.thread_id = response[0].thread_id if response else "GMAT IR, Error! thread_id not found for TPA (questionComponent@l:131)"
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return self.thread_id, message["part1"], message["part2"], message["question"], message["type"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionText is: \n{response[0].content[0].text.value}\n\n")
            return "", "", "", "", ""
    def generate_QuestionTitle(self):
        response = self.llm.invoke({"content":f"QuestionTitle", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionTitle is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionSolution(self):
        response = self.llm.invoke({"content":f"QuestionSolution", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["solution"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionSolution is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionOptions(self):
        response = self.llm.invoke({"content":f"QuestionOptions", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["options"], message["answer"]
        except Exception as e:
            print(f"GMAT IR, Error: message received for QuestionOptions is: \n{response[0].content[0].text.value}\n\n")
            return [], ""