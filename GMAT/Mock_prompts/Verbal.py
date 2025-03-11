# 
import json, os, random

class Verbal_prompts: 
   def __init__(self, mock_difficulty):
      self.mock_difficulty = mock_difficulty
      self.total_questions = 23

      with open(os.path.join(os.path.dirname(__file__), "jsonfiles", "difficulty_distribution.json"), "r") as file:
         self.difficulty_distribution = json.load(file)["verbal"]

      with open(os.path.join(os.path.dirname(__file__), "jsonfiles", "component_allocation.json"), "r") as file:
         self.complete_component_allocation = json.load(file)
         self.component_allocation = self.complete_component_allocation["verbal"]
      self.combination_number = self.component_allocation["combination_number"]
      self.themes = self.component_allocation["themes"]
      self.cr_types = self.component_allocation["cr_types"]

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
      print(f"difficulty pool length:- {len(difficulty_pool)} it should be 20, always")
      random.shuffle(difficulty_pool)
      return difficulty_pool
   

   def generate_question_prompts(self):
         difficulty_pool = self.get_difficulty_pool()
         prompts = []
         cn = self.combination_number
         itr = random.randint(0,1)
         num_rc_questions = self.component_allocation["section"]["RC"][itr]
         num_cr_questions = self.component_allocation["section"]["CR"][itr]
         rcs = []
         if num_rc_questions == 13:
            rcs = ["RC_3", "RC_3", "RC_3", "RC_4"]
         else:
            rcs = ["RC_3", "RC_3", "RC_4", "RC_4"]
         random.shuffle(rcs)
         for rc in rcs:
            theme = self.themes[cn%len(self.themes)]
            cn+=1
            
            if cn % len(self.themes):
               random.shuffle(self.themes)
            prompts.append(f"<{theme}> - <{rc}> - <difficulty_level: {difficulty_pool.pop()}>")
         for cr in range(num_cr_questions):
            theme = self.themes[cn%len(self.themes)]
            cn+=1
            cr_type = self.cr_types[(cn%len(self.themes))%len(self.cr_types)]
            cn+=1
            if cn % len(self.themes):
               random.shuffle(self.themes)
            if cn % len(self.cr_types):
               random.shuffle(self.cr_types)
            prompts.append(f"<{theme}> - <CR> - <{cr_type}> - <difficulty_level: {difficulty_pool.pop()}>")
         random.shuffle(prompts)
         self.combination_number += 1
         self.component_allocation["combination_number"] = self.combination_number
         self.component_allocation["themes"] = self.themes
         self.component_allocation["cr_types"] = self.cr_types
         self.complete_component_allocation["verbal"] = self.component_allocation
         with open(os.path.join(os.path.dirname(__file__), "jsonfiles", "component_allocation.json"), "w") as file:
            json.dump(self.complete_component_allocation, file)
         return prompts
   
# v = Verbal(1)
# prompts = v.generate_question_prompts()
# for prompt in prompts:
#    print(prompt)
# print(f"length of prompts: {len(prompts)}")