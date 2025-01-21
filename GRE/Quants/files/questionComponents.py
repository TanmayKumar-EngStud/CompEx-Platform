import json, re

def refine_response(response_text):
    try:
        # First try to parse as JSON directly
        try:
            json.loads(response_text)
            return response_text  # Return string instead of parsed object
        except json.JSONDecodeError:
            pass

        # Look for JSON-like structure between curly braces
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON structure found")
        
        json_string = json_match.group(0).strip()
        
        # Handle LaTeX expressions
        def escape_latex(match):
            latex = match.group(1)
            latex = latex.replace('\\', '\\\\')  # Escape backslashes
            return f'~~{latex}~~'
            
        json_string = re.sub(r'~~(.*?)~~', escape_latex, json_string)
        
        # Clean up whitespace and handle quotes
        json_string = re.sub(r"'", '"', json_string)  # Replace single quotes with double quotes
        
        # Validate final JSON
        try:
            json.loads(json_string)
            return json_string
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON validation failed: {str(e)}")
            
    except Exception as e:
        print(f"Error in refine_response: {str(e)}")
        return None

class ParentChildQuestion:
    def __init__(self, llm, prompt, thread_id=None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id
    def generate_questionGraph(self):
        response = self.llm.invoke({"content":f"questionGraph: {self.prompt}"})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            self.thread_id = response[0].thread_id if response else "GRE Quants, Error! thread_id not found! (questionComponent@l:115)"
            return self.thread_id, message["graph/table"]
        except Exception as e:
            print(f"GRE Quants, Error: message received for questionGraph is: \n{response[0].content[0].text.value}\n\n")
            return "", ""
    def generate_parentTitle(self):
        response = self.llm.invoke({"content": f"ParentTitle", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            print(f"GRE Quants, Error: message received for parentChildQuestion(generate_parentTitle) is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_childQuestionTitle(self, index):
        response = self.llm.invoke({"content": f"ChildQuestionTitle: {index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            print(f"GRE Quants, Error: message received for parentChildQuestion(generate_childQuestionTitle) is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_childQuestion(self, index, child_prompt=""):
        response = self.llm.invoke({"content": f"ChildQuestion: {index} of {child_prompt}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["question"]
        except Exception as e:
            print(f"GRE Quants, Error: message received for parentChildQuestion(generate_childQuestion) is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_childOptions(self, index):
        response = self.llm.invoke({"content": f"ChildOptions: {index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["options"], message["answer"]
        except Exception as e:
            print(f"GRE Quants, Error: message received for parentChildQuestion(generate_childOptions) is: \n{response[0].content[0].text.value}\n\n")
            return []
    def generate_childSolution(self, index):
        response = self.llm.invoke({"content": f"ChildSolution: {index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["solution"]
        except Exception as e:
            print(f"GRE Quants, Error: message received for parentChildQuestion(generate_childSolution) is: \n{response[0].content[0].text.value}\n\n")
            return ""

class SimpleQuestion:
    def __init__(self, llm, prompt, thread_id= None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id
    def generate_questionText(self):
        response = self.llm.invoke({"content":f"QuestionText: {self.prompt}"})
        try:
            response_text = refine_response([message.content[0].text.value for message in response][0])
            message = json.loads(response_text)
            self.thread_id = response[0].thread_id if response else "GRE Quants, Error! thread_id not found! (questionComponent@l:30)"
            return self.thread_id, message["question"]
        except Exception as e:
            print(f"GRE Quants, Error: message received for questionText is: \n{[message.content[0].text.value for message in response][0]}\n\n")
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
            print(f"GRE Quants, Error: message received for questionTitle is: \n{[message.content[0].text.value for message in response][0]}\n\n")
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
            print(f"GRE Quants, Error: message received for questionSolution is: \n{response[0].content[0].text.value}\n\n")
            print(f"JSON parsing error: {str(e)}")
            return ""
    def generate_questionOptions(self):
      response = self.llm.invoke({"content":f"QuestionOptions", "thread_id": self.thread_id})
      try:
         raw_response = response[0].content[0].text.value
         json_string = refine_response(raw_response.replace("'", '"'))
         message = json.loads(json_string)
         
         return message["options"], message["answer"]
      except Exception as e:
         print(f"GRE Quants, Error: message received for questionOptions is: \n{response[0].content[0].text.value}\n\n")
         print(f"JSON parsing error: {str(e)}")
         return [], ""
      
class DataSufficiencyQuestion:
    def __init__(self, llm, prompt, thread_id= None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id
    def generate_questionGraph(self):
        response = self.llm.invoke({"content":f"questionGraph: {self.prompt}"})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            self.thread_id = response[0].thread_id if response else "GRE Quants, Error! thread_id not found! (questionComponent@l:115)"
            return self.thread_id, message["graph/table"]
        except Exception as e:
            print(f"GRE Quants, Error: message received for questionGraph is: \n{response[0].content[0].text.value}\n\n")
            return "", ""
    def generate_questionText(self):
        if(self.thread_id is not None):
            response = self.llm.invoke({"content":f"QuestionText: {self.prompt}", "thread_id": self.thread_id})
        else:
            response = self.llm.invoke({"content":f"QuestionText: {self.prompt}"})
            self.thread_id = response[0].thread_id if response else "GRE Quants, Error! thread_id not found! (questionComponent@l:125)"
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return self.thread_id, message["question"], message["statements"]
        except Exception as e:
            print(f"GRE Quants, Error: message received for questionText is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_questionTitle(self):
        response = self.llm.invoke({"content":f"QuestionTitle", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            print(f"GRE Quants, Error: message received for questionTitle is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_questionSolution(self):
        response = self.llm.invoke({"content":f"QuestionSolution", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["solution"], str(message["answer"])
        except Exception as e:
            print(f"GRE Quants, Error: message received for questionSolution is: \n{response[0].content[0].text.value}\n\n")
            return "", ""