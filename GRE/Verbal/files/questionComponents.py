import json, re

# childQuestionText, childQuestionSolution, childQuestionOptions, childQuestionTitle 
# QuestionText, QuestionTitle, QuestionSolution, QuestionOptions

def refine_response(response_text): 
    json_string = response_text.replace("'", "\'")
    json_string = re.sub(r',\s*]', '}', json_string)
    json_string = re.sub(r',\s*}', ']', json_string)
    return json_string

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
        response = self.llm.invoke({"content":f"QuestionText: {input_data}"})
        try:
            response_text = refine_response([message.content[0].text.value for message in response][0])
            print(f"the response text is: {response_text}")
            message = json.loads(response_text)
            
            thread_id = response[0].thread_id if response else "error! thread_id not found! (questionComponent@l:30)"
            return thread_id, message["question"]
        except Exception as e:
            print(f"Error: message received for questionText is: \n{[message.content[0].text.value for message in response][0]}\n\n")
            print(f"Exception details: {str(e)}")
            return "", ""

class QuestionTitle:
    def __init__(self, llm, thread_id):
        self.llm = llm
        self.thread_id = thread_id

    def generate_questionTitle(self):
        response = self.llm.invoke({"content":f"QuestionTitle", "thread_id": self.thread_id})
        try:
            response_text = refine_response([message.content[0].text.value for message in response][0])
            message = json.loads(response_text)
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
        response = self.llm.invoke({"content":f"QuestionSolution", "thread_id": self.thread_id})
        try:
            response_text = refine_response([message.content[0].text.value for message in response][0])
            if isinstance(response_text, dict):
                message = response_text
            else:
                message = json.loads(response_text)    
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
      response = self.llm.invoke({"content":f"QuestionOptions: {num_options}", "thread_id": self.thread_id})
      try:
         raw_response = response[0].content[0].text.value
         json_string = refine_response(raw_response)
         message = json.loads(json_string)
         options = [str(opt) for opt in message["options"]]
         return options
      except Exception as e:
         print(f"Error: message received for questionOptions is: \n{response[0].content[0].text.value}\n\n")
         print(f"JSON parsing error: {str(e)}")
         return []