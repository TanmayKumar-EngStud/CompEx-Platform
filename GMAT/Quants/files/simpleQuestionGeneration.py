import random
from Quants.files.questionComponents import SimpleQuestion

class SimpleQuestionGeneration:
   def __init__(self, llm, prompt):
      self.llm = llm
      self.prompt = prompt
      self.questionData = {}
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

   def getTagAtIndex(self, indexes):
      try:
         tags = []
         for index in indexes:
            tags.extend([x.strip() for x in self.prompt.split(" - ")[index].strip("<>").strip("[]").split(",")])
         return tags
      except Exception as e:
         print(f"Error getting tags: {str(e)}")
         return ["GMAT Quants"]
   
   def generate_question(self):
      try:
         questionContent = SimpleQuestion(self.llm)
         
         # Generate question text
         thread_id, question = questionContent.generate_questionText(self.prompt)
         if not thread_id or not question:
            raise Exception("Failed to generate valid question text")
         self.questionData["thread_id"] = thread_id
         self.questionData["question"] = question
         
         # Generate title
         title = questionContent.generate_questionTitle()
         self.questionData["title"] = title if title else "GMAT Quants Question"
         
         # Generate solution
         solution = questionContent.generate_questionSolution()
         self.questionData["solution"] = solution if solution else "Solution not available"
         
         # Generate options and answer
         options, answer = questionContent.generate_questionOptions()
         if options:
            options_list = list(options.values())
            random.shuffle(options_list)
            self.questionData["options"] = options_list
            self.questionData["answer"] = options[answer] if answer in options else options_list[0]
         else:
            self.questionData["options"] = ["A", "B", "C", "D"]
            self.questionData["answer"] = "A"
         
         # Set difficulty and tags
         try:
            self.questionData["difficulty"] = int(self.prompt.split(" - ")[2].strip("<>"))
         except:
            self.questionData["difficulty"] = 1
            
         self.questionData["tags"] = self.getTagAtIndex([0, 1, 3])
         
         return self.questionData
         
      except Exception as e:
         print(f"Error in generate_question: {str(e)}")
         # Return a default structure if generation fails
         return {
            "thread_id": "",
            "question": "Error generating question",
            "title": "GMAT Quants Question",
            "solution": "Solution not available",
            "options": ["A", "B", "C", "D"],
            "answer": "A",
            "difficulty": 1,
            "tags": ["GMAT Quants"],
            "prompt": self.prompt
         }
