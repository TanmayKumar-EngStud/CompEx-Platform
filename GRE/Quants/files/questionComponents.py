import json
class QuestionGraph:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt

    def generate_questionGraph(self):
        response = self.llm.invoke({"content":f"questionGraph: {self.prompt}"})
        try:
            message = json.loads([message.content[0].text.value for message in response][0])
            return response[0].thread_id, message["graph/table"]
        except Exception as e:
            print(f"Error: message received for questionGraph is: \n{response[0].content[0].text.value}\n\n")
            return "", ""

class ChildQuestionText:
    def __init__(self, llm, prompt, thread_id):
        self.llm = llm
        self.prompt = prompt
        self.thread_id = thread_id

    def generate_childQuestionText(self, index):
        print(f"the thread id is: {self.thread_id}")
        response = self.llm.invoke({"content":f"childQuestionText: Question {index} of {self.prompt}", "thread_id": self.thread_id})
        try:
            message = json.loads([message.content[0].text.value for message in response][0])
            return message["question"]
        except Exception as e:
            print(f"Error: message received for childQuestionText is: \n{response[0].content[0].text.value}\n\n")
            return ""
class ChildQuestionSolution:
    def __init__(self, llm, thread_id):
        self.llm = llm
        self.thread_id = thread_id
    def generate_childQuestionSolution(self, question_number):
        response = self.llm.invoke({"content":f"mode:- childQuestionSolution; question: {question_number}", "thread_id": self.thread_id})
        try:
            message = json.loads([message.content[0].text.value for message in response][0])

            return message["solution"], str(message["answer"])
        except Exception as e:
            print(f"Error: message received for childQuestionSolution is: \n{response[0].content[0].text.value}\n\n")
            return "", ""

class QuestionText:
    def __init__(self, llm, thread_id= None):
        self.llm = llm
        self.thread_id = thread_id

    def generate_questionText(self, input_data):
        response= None
        if(self.thread_id is not None):
            response = self.llm.invoke({"content":f"questionText: {input_data}", "thread_id": self.thread_id})
        else:
            response = self.llm.invoke({"content":f"questionText: {input_data}"})
        try:
            message = json.loads([message.content[0].text.value for message in response][0])
            thread_id = response[0].thread_id if response else "error! thread_id not found! (questionComponent@l:30)"
            return thread_id, message["question"]
        except Exception as e:
            # message received is:
            print(f"Error: message received for questionText is: \n{[message.content[0].text.value for message in response][0]}\n\n")
            return "", ""

class QuestionTitle:
    def __init__(self, llm, thread_id):
        self.llm = llm
        self.thread_id = thread_id

    def generate_questionTitle(self):
        response = self.llm.invoke({"content":f"questionTitle", "thread_id": self.thread_id})
        try:
            message = json.loads([message.content[0].text.value for message in response][0])
            return message["title"]
        except Exception as e:
            # message received is:
            print(f"Error: message received for questionTitle is: \n{[message.content[0].text.value for message in response][0]}\n\n")
            return ""

class QuestionSolution:
    def __init__(self, llm, thread_id):
        self.llm = llm
        self.thread_id = thread_id

    def generate_questionSolution(self):
        response = self.llm.invoke({"content":f"questionSolution", "thread_id": self.thread_id})
        try:
            raw_response = response[0].content[0].text.value
            json_string = raw_response.replace("'", '"')
            message = json.loads(json_string)
            return message["solution"], str(message["answer"])
        except Exception as e:
            print(f"Error: message received for questionSolution is: \n{response[0].content[0].text.value}\n\n")
            print(f"JSON parsing error: {str(e)}")
            return "", ""
    
class QuestionOptions:
   def __init__(self, llm, thread_id):
      self.llm = llm
      self.thread_id = thread_id

   def generate_questionOptions(self, num_options=4):
      response = self.llm.invoke({"content":f"questionOptions: {num_options}", "thread_id": self.thread_id})
      try:
         raw_response = response[0].content[0].text.value
         json_string = raw_response.replace("'", '"')
         message = json.loads(json_string)
         options = [str(opt) for opt in message["options"]]
         return options
      except Exception as e:
         print(f"Error: message received for questionOptions is: \n{response[0].content[0].text.value}\n\n")
         print(f"JSON parsing error: {str(e)}")
         return []