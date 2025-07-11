import json, os, random

class Quants_prompts:
   def __init__(self, mock_difficulty):
      self.mock_difficulty = mock_difficulty
      self.total_questions = 21

      with open(os.path.join(os.path.dirname(__file__), "../../system_instructions/gmat/difficulty_distribution.json"), "r") as file:
         self.difficulty_distribution = json.load(file)["quants"]

      with open(os.path.join(os.path.dirname(__file__), "../../system_instructions/gmat/component_allocation.json"), "r") as file:
         self.complete_component_allocation = json.load(file)
         self.component_allocation = self.complete_component_allocation["quants"]

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
         cn = self.component_allocation["combination_number"]
         prompt_elements = []
         question_style = self.component_allocation["question_style"][cn%len(self.component_allocation["question_style"])]
         if cn%len(self.component_allocation["question_style"]) == 0:
            random.shuffle(self.component_allocation["question_style"])
         prompt_elements.append(question_style)
         
         option = self.component_allocation["options"][cn%len(self.component_allocation["options"])]
         if cn%len(self.component_allocation["options"]) == 0:
            random.shuffle(self.component_allocation["options"])
         prompt_elements.append(option)
         
         focused_skill = self.component_allocation[option]["focused_skill"][cn%len(self.component_allocation[option]["focused_skill"])]
         if cn%len(self.component_allocation[option]["focused_skill"]) == 0:
            random.shuffle(self.component_allocation[option]["focused_skill"])
         prompt_elements.append(focused_skill)
         
         topics = self.component_allocation[option]["topics"][cn%len(self.component_allocation[option]["topics"])]
         if cn%len(self.component_allocation[option]["topics"]) == 0:
            random.shuffle(self.component_allocation[option]["topics"])
         prompt_elements.append(topics)
         
         if option == "Word Problems":
            theme = self.component_allocation[option]["themes"][cn%len(self.component_allocation[option]["themes"])]
            if cn%len(self.component_allocation[option]["themes"]) == 0:
               random.shuffle(self.component_allocation[option]["themes"])
            prompt_elements.append(theme)
         
         prompt_elements.append(f"difficulty_level: {difficulty_pool.pop()}")
         prompt = " - ".join(f"<{element}>" for element in prompt_elements)
         self.component_allocation["combination_number"] += 1
         prompts.append(prompt)

      self.complete_component_allocation["quants"] = self.component_allocation
      with open(os.path.join(os.path.dirname(__file__), "../../system_instructions/gmat/component_allocation.json"), "w") as file:
         json.dump(self.complete_component_allocation, file, indent=4)
      return prompts

# q = Quants(5)
# prompts = q.generate_question_prompts()
# for prompt in prompts:
#    print(prompt)
# print("-"*80)
# print(f"total prompts: {len(prompts)}")