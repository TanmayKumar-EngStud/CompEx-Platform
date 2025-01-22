import json, re

def refine_response(response_text):
    try:
        # First try to parse as JSON directly
        try:
            json.loads(response_text)
            return response_text
        except json.JSONDecodeError:
            pass

        # Look for JSON-like structure between curly braces
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            return None
        
        json_string = json_match.group(0).strip()
        
        # Handle LaTeX expressions
        latex_expressions = []
        def replace_latex(match):
            expr = match.group(1)
            # Double escape backslashes in LaTeX
            expr = expr.replace('\\', '\\\\')
            latex_expressions.append(expr)
            return f"__LATEX_{len(latex_expressions)-1}__"
        
        json_string = re.sub(r'~~(.*?)~~', replace_latex, json_string)
        
        # Clean up whitespace but preserve newlines
        json_string = re.sub(r'[ \t]+', ' ', json_string)
        
        # Handle quotes and formatting
        json_string = json_string.replace('\\"', '__ESCAPED_QUOTE__')
        json_string = re.sub(r"'", '"', json_string)  # Replace single quotes
        json_string = re.sub(r',(\s*[}\]])', r'\1', json_string)  # Clean trailing commas
        
        # Restore LaTeX expressions
        for i, expr in enumerate(latex_expressions):
            json_string = json_string.replace(f'__LATEX_{i}__', f'~~{expr}~~')
        
        # Restore escaped quotes
        json_string = json_string.replace('__ESCAPED_QUOTE__', '\\"')
        
        # Validate final JSON
        try:
            json.loads(json_string)
            return json_string
        except json.JSONDecodeError as e:
            print(f"JSON parsing error after cleanup: {str(e)}")
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
        response = self.llm.invoke({"content":f"MainQuestionTitle (based on the given question data what would be a unique question title of complete Multiple Source Reasoning question)", "thread_id": self.thread_id})
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