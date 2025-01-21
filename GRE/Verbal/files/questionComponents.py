import json, re

def refine_response(response_text):
    # First try direct JSON parsing
    try:
        json.loads(response_text)
        return response_text
    except json.JSONDecodeError:
        pass

    # Extract JSON structure and clean whitespace
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if not json_match:
        raise ValueError("No JSON structure found")
    
    json_string = json_match.group(0)
    json_string = re.sub(r'\s+', ' ', json_string.strip())
    
    # Handle LaTeX expressions
    latex_expressions = []
    def replace_latex(match):
        expr = match.group(1)
        expr = expr.replace('\\', '\\\\').replace('"', '\\"')
        latex_expressions.append(expr)
        return f"__LATEX_{len(latex_expressions)-1}__"
    
    json_string = re.sub(r'~~(.*?)~~', replace_latex, json_string)
    
    # Handle quotes and cleanup
    json_string = json_string.replace('\\"', '__ESCAPED_QUOTE__')
    json_string = re.sub(r'(?<!\\)"', '\\"', json_string)
    json_string = re.sub(r"(?<!\\)'", '"', json_string)
    json_string = re.sub(r',(\s*[}\]])', r'\1', json_string)
    
    # Restore LaTeX expressions
    for i, expr in enumerate(latex_expressions):
        json_string = json_string.replace(f'__LATEX_{i}__', f'~~{expr}~~')
    
    json_string = json_string.replace('__ESCAPED_QUOTE__', '\\"')
    
    # Validate and return
    json.loads(json_string)
    return json_string

class ParentChildQuestion:
    def __init__(self, llm, prompt, thread_id=None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id
    def generate_passages(self):
        response = self.llm.invoke({"content": f"ParentQuestion: {self.prompt}"})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            self.thread_id = response[0].thread_id if response else "error! thread_id not found! (Verbal/files/questionComponent@l:17)"
            return message["passages"]
        except Exception as e:
            print(f"GRE Verbal, Error: message received for parentChildQuestion(generate_passages) is: \n{response[0].content[0].text.value}\n\n")
            return []
    def generate_parentTitle(self):
        response = self.llm.invoke({"content": f"ParentTitle", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["title"]
        except Exception as e:
            print(f"GRE Verbal, Error: message received for parentChildQuestion(generate_parentTitle) is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_childQuestion(self, index, child_prompt=""):
        response = self.llm.invoke({"content": f"ChildQuestion: {index} of {child_prompt}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["question"]
        except Exception as e:
            print(f"GRE Verbal, Error: message received for parentChildQuestion(generate_childQuestion) is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_childOptions(self, index):
        response = self.llm.invoke({"content": f"ChildOptions: {index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["options"], message["answer"]
        except Exception as e:
            print(f"GRE Verbal, Error: message received for parentChildQuestion(generate_childOptions) is: \n{response[0].content[0].text.value}\n\n")
            return {}, ""
    def generate_childSolution(self, index):
        response = self.llm.invoke({"content": f"ChildSolution: {index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["solution"]
        except Exception as e:
            print(f"GRE Verbal, Error: message received for parentChildQuestion(generate_childSolution) is: \n{response[0].content[0].text.value}\n\n")
            return ""

class SimpleQuestion:
    def __init__(self, llm, thread_id= None):
        self.llm = llm
        self.thread_id = thread_id
    def generate_questionText(self, input_data):
        response = self.llm.invoke({"content":f"QuestionText: {input_data}"})
        try:
            response_text = refine_response([message.content[0].text.value for message in response][0])
            message = json.loads(response_text)
            self.thread_id = response[0].thread_id if response else "error! thread_id not found! (questionComponent@l:30)"
            return self.thread_id, message["question"]
        except Exception as e:
            print(f"GRE Verbal, Error: message received for questionText is: \n{[message.content[0].text.value for message in response][0]}\n\n")
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
            print(f"GRE Verbal, Error: message received for questionTitle is: \n{[message.content[0].text.value for message in response][0]}\n\n")
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
            print(f"GRE Verbal, Error: message received for questionSolution is: \n{response[0].content[0].text.value}\n\n")
            print(f"JSON parsing error: {str(e)}")
            return ""
    def generate_questionOptions(self, num_options=4):
      response = self.llm.invoke({"content":f"QuestionOptions: {num_options}", "thread_id": self.thread_id})
      try:
         raw_response = response[0].content[0].text.value
         json_string = refine_response(raw_response)
         message = json.loads(json_string)
         return message["options"], message["answer"]
      except Exception as e:
         print(f"GRE Verbal, Error: message received for questionOptions is: \n{response[0].content[0].text.value}\n\n")
         print(f"JSON parsing error: {str(e)}")
         return {}, ""