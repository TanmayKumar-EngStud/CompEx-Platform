import json, os, random

class Integrated_Reasoning_prompts:
   def __init__(self, mock_difficulty):
      self.mock_difficulty = mock_difficulty
      with open(os.path.join(os.path.dirname(__file__), "jsonfiles", "difficulty_distribution.json"), "r") as file:
         self.difficulty_distribution = json.load(file)["integrated_reasoning"]
      
      with open(os.path.join(os.path.dirname(__file__), "jsonfiles", "component_allocation.json"), "r") as file:
         self.complete_component_allocation = json.load(file)
         self.component_allocation = self.complete_component_allocation["integrated_reasoning"]
      self.total_questions = self.component_allocation["total_questions"]
      self.remaining_questions = 12
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

      # MSR - 1 PQ
      total_child_questions = random.choice(self.component_allocation["MSR"]["total_child_questions"])
      question_style = random.choice(self.component_allocation["MSR"]["question_style"])
      focused_skill = random.choice(self.component_allocation["MSR"]["focused_skill"])
      theme = random.choice(self.component_allocation["MSR"]["themes"])
      question_prompt = f"MSR - <total_child_questions: {total_child_questions}> - <{theme}> - <{focused_skill}> - <{question_style}> - <difficulty_level: {difficulty_pool.pop()}>"
      prompts.append(question_prompt)
      self.remaining_questions -= total_child_questions
      # TPA - 1 PQ
      total_child_questions = 2
      theme = random.choice(self.component_allocation["TPA"]["themes"])
      focused_skill = random.choice(self.component_allocation["TPA"]["focused_skill"])
      type = random.choice(self.component_allocation["TPA"]["type"])
      question_prompt = f"TPA - <{theme}> - <{focused_skill}> - <{type}> - <difficulty_level: {difficulty_pool.pop()}>"
      prompts.append(question_prompt)
      self.remaining_questions -= total_child_questions
      
      total_ta = random.choice([2,3])
      for _ in range(total_ta):
         focused_skill = random.choice(self.component_allocation["TA"]["focused_skill"])
         table_type = random.choice(self.component_allocation["TA"]["table_type"])
         theme = random.choice(self.component_allocation["TA"]["themes"])
         type = random.choice(self.component_allocation["TA"]["type"])
         question_prompt = f"TA - <{theme}> - <{focused_skill}> - <{table_type}> - <{type}> - <difficulty_level: {difficulty_pool.pop()}>"
         prompts.append(question_prompt)
      self.remaining_questions -= total_ta
      
      total_gi = 12 - self.remaining_questions
      for _ in range(total_gi):
         focused_skill = random.choice(self.component_allocation["GI"]["focused_skill"])
         chart_type = random.choice(self.component_allocation["GI"]["chart_type"])
         theme = random.choice(self.component_allocation["GI"]["themes"])
         question_prompt = f"GI - <{theme}> - <{focused_skill}> - <{chart_type}> - <difficulty_level: {difficulty_pool.pop()}>"
         prompts.append(question_prompt)
      self.remaining_questions -= total_gi
      
      total_ds = 8
      print(f"difficuty_level:- {difficulty_pool}\n length remaining:- {len(difficulty_pool)}")
      for _ in range(total_ds):
         topic = random.choice(self.component_allocation["DS"]["topics"])
         focused_skill = random.choice(self.component_allocation["DS"]["focused_skill"])
         question_prompt = f"DS - <{topic}> - <{focused_skill}> - <difficulty_level: {difficulty_pool.pop()}>"
         prompts.append(question_prompt)
      self.remaining_questions -= total_ds
      
      return prompts

# ir = Integrated_Reasoning(1)
# prompts = ir.generate_question_prompts()
# for i in prompts:
#    print(i)
