import json, os, random

class Quants_prompts:
   def __init__(self, mock_difficulty):
      self.mock_difficulty = mock_difficulty
      self.total_questions = 21

      with open(os.path.join(os.path.dirname(__file__), "../../system_instructions/gmat/difficulty_distribution.json"), "r") as file:
         self.difficulty_distribution = json.load(file)["quants"]

      with open(os.path.join(os.path.dirname(__file__), "../../system_instructions/gmat/customizations.json"), "r") as file:
         self.complete_customizations = json.load(file)
         self.customizations = self.complete_customizations["quants"]

   def get_difficulty_pool(self) -> list[int]:
      difficulty_ratio = self.difficulty_distribution[str(self.mock_difficulty)]
      total_questions = self.total_questions + 5
      easy_count = int(total_questions * difficulty_ratio["easy"])
      medium_count = int(total_questions * difficulty_ratio["medium"])
      hard_count = total_questions - (easy_count + medium_count)
      one = random.randint(1, easy_count-1)
      three = random.randint(1, medium_count-1)
      five = random.randint(1, hard_count-1)
      two_three = random.randint(1, medium_count - three)
      two = easy_count - one + two_three
      four = hard_count - five + medium_count - three - two_three
      difficulty_pool = ([1]*one + [2]*two + [3]*three + [4]*four + [5]*five)
      # print(f"difficulty pool length:- {len(difficulty_pool)} it should be 20, always")
      random.shuffle(difficulty_pool)
      return difficulty_pool
   
   
   def generate_question_prompts(self):
      difficulty_pool = self.get_difficulty_pool()
      prompts = []
      
      for i in range(self.total_questions):
         prompt_elements = []
         
         # Generate DS or PS questions based on distribution
         if i < self.customizations["Data_Sufficiency"]:
            # Data Sufficiency nomenclature: "DS - <questionTopic> - <questionTheme> - <questionStyle> - <graphType/tableType> - <focused_skill> - <difficulty_level: {1-5}>"
            # graphType/tableType is optional (can be None)
            question_type = "DS"
            topic = random.choice(self.customizations["data sufficiency"]["questionTopic"])
            theme = random.choice(self.customizations["data sufficiency"]["questionTheme"])
            question_style = random.choice(self.customizations["data sufficiency"]["questionStyle"])
            graph_table_type = random.choice(self.customizations["data sufficiency"]["graphType/tableType$"])
            focused_skill = random.choice(self.customizations["data sufficiency"]["focused_skill"])
            
            prompt_elements = [question_type, topic, theme, question_style]
            if graph_table_type is not None:
               prompt_elements.append(graph_table_type)
            prompt_elements.extend([focused_skill, f"difficulty_level: {difficulty_pool.pop()}"])
         else:
            # Problem Solving nomenclature: "S - <questionTopic> - <questionTheme> - <questionStyle> - <graphType/tableType> - <focused_skill> - <difficulty_level: {1-5}>"
            # graphType/tableType is optional (can be None)
            question_type = "S"
            topic = random.choice(self.customizations["problem solving"]["questionTopic"])
            theme = random.choice(self.customizations["problem solving"]["questionTheme&"])
            question_style = random.choice(self.customizations["problem solving"]["questionStyle"])
            graph_table_type = random.choice(self.customizations["problem solving"]["graphType/tableType*"])
            focused_skill = random.choice(self.customizations["problem solving"]["focused_skill"])
            
            prompt_elements = [question_type, topic, theme, question_style]
            if graph_table_type is not None:
               prompt_elements.append(graph_table_type)
            prompt_elements.extend([focused_skill, f"difficulty_level: {difficulty_pool.pop()}"])
         
         prompt = " - ".join(f"<{element}>" for element in prompt_elements)
         prompts.append(prompt)

      # No need to write back to customizations.json as it's a read-only config
      return prompts

# q = Quants(5)
# prompts = q.generate_question_prompts()
# for prompt in prompts:
#    print(prompt)
# print("-"*80)
# print(f"total prompts: {len(prompts)}")