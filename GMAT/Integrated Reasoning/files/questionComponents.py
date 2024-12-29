import json, re

def refine_response(response_text): 
    json_string = re.sub(r'\s+', ' ', response_text.strip())
    json_string = json_string.replace('\\', '\\\\')
    json_string = re.sub(r',\s*}', '}', json_string)
    json_string = re.sub(r',\s*]', ']', json_string)
    return json_string
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
            self.thread_id = response[0].thread_id if response else "error! thread_id not found for GI (questionComponent@l:131)"
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return self.thread_id, message["graphs"]
        except Exception as e:
            print(f"Error: message received for questionGraph is: \n{response[0].content[0].text.value}\n\n")
            return "", ""
    def generate_questionText(self):
        response = self.llm.invoke({"content":f"QuestionText", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["question"]
        except Exception as e:
            print(f"Error: message received for questionText is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_questionSolution(self):
        response = self.llm.invoke({"content":f"QuestionSolution", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["solution"], str(message["answer"])
        except Exception as e:
            print(f"Error: message received for questionSolution is: \n{response[0].content[0].text.value}\n\n")
            return "", ""
    def generate_questionOptions(self):
        response = self.llm.invoke({"content":f"QuestionOptions", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["options"]
        except Exception as e:
            print(f"Error: message received for questionOptions is: \n{response[0].content[0].text.value}\n\n")
            return []

class MSR: 
    def __init__(self, llm, prompt, thread_id= None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id

    def generate_SourceInfo(self, source_index):
        if(self.thread_id):
            response = self.llm.invoke({"content":f"SourceInfo_{source_index}", "thread_id": self.thread_id})
        else:
            response = self.llm.invoke({"content":f"SourceInfo_{source_index}"})
            self.thread_id = response[0].thread_id if response else "error! thread_id not found for MSR (questionComponent@l:131)"
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["source"]
        except Exception as e:
            print(f"Error: message received for SourceInfo_{source_index} is: \n{response[0].content[0].text.value}\n\n")
            return ""
        
    def generate_QuestionText(self, question_index):
        response = self.llm.invoke({"content":f"QuestionText_{question_index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["question"]
        except Exception as e:
            print(f"Error: message received for QuestionText_{question_index} is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionSolution(self, question_index):
        response = self.llm.invoke({"content":f"QuestionSolution_{question_index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["solution"], str(message["answer"])
        except Exception as e:
            print(f"Error: message received for QuestionSolution_{question_index} is: \n{response[0].content[0].text.value}\n\n")
            return "", ""
    def generate_QuestionOptions(self, question_index):
        response = self.llm.invoke({"content":f"QuestionOptions_{question_index}", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["options"]
        except Exception as e:
            print(f"Error: message received for QuestionOptions_{question_index} is: \n{response[0].content[0].text.value}\n\n")
            return []

class TA:
    def __init__(self, llm, prompt, thread_id= None):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id
    def generate_QuestionTable(self):
        response = self.llm.invoke({"content":f"QuestionTable", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["table"]
        except Exception as e:
            print(f"Error: message received for QuestionTable is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionText(self):
        response = self.llm.invoke({"content":f"QuestionText", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["question"]
        except Exception as e:
            print(f"Error: message received for QuestionText is: \n{response[0].content[0].text.value}\n\n")
            return ""
    def generate_QuestionOptions(self):
        response = self.llm.invoke({"content":f"QuestionOptions", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["options"]
        except Exception as e:
            print(f"Error: message received for QuestionOptions is: \n{response[0].content[0].text.value}\n\n")
            return []
    def generate_QuestionSolution(self):
        response = self.llm.invoke({"content":f"QuestionSolution", "thread_id": self.thread_id})
        try:
            message = json.loads(refine_response([message.content[0].text.value for message in response][0]))
            return message["solution"], str(message["answer"])
        except Exception as e:
            print(f"Error: message received for QuestionSolution is: \n{response[0].content[0].text.value}\n\n")
            return "", ""