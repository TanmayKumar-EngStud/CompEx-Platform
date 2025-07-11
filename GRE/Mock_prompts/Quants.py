
import json, os, random

class Quants_prompts:
   def __init__(self, mock_difficulty):
      self.mock_difficulty = mock_difficulty
      self.total_questions = 27

      
      with open(os.path.join(os.path.dirname(__file__), "../../system_instructions/gre/difficulty_distribution.json"), "r") as file:
         self.difficulty_distribution = json.load(file)["quants"]

      with open(os.path.join(os.path.dirname(__file__), "../../system_instructions/gre/component_allocation.json"), "r") as file:
         self.complete_component_allocation = json.load(file)
         self.component_allocation = self.complete_component_allocation["quants"]
      
      self.section_1 = self.component_allocation["section1"]
      self.section_2 = self.component_allocation["section2"]
      self.sections = [self.section_1, self.section_2]

   def prepare_difficulty_pool(self, total_questions):
      difficulty_ratio = self.difficulty_distribution[str(self.mock_difficulty)]
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
      random.shuffle(difficulty_pool)
      return difficulty_pool

   def generate_prompt(self, difficulty, qStyle, qType = "simple"):
      # qStyle = "ds", "mcq_single", "mcq_multiple", "ne"
      # qType2 = "simple", "parent_child"

      primary_qType = qType if qType == "simple" else "parent_child"
      with open(os.path.join(os.path.dirname(__file__), "../../system_instructions/gre/combination.json"), "r") as file:
         parameters = json.load(file)[qStyle][primary_qType]
      elements = []

      for value in parameters.values():
         elements.append(f"<{random.choice(value)}>")
      prompt = {f"{qStyle} {qType}":" - ".join(elements)+ f"- <difficulty-level: {difficulty}>"}
      return prompt
   
   def generate_question_prompts(self) -> list[str]:
      all_prompts = []
      for section in self.sections:
         section_prompts = []
         mcq_single = section["MCQ_Single"]
         mcq_multiple = section["MCQ_Multiple"]
         ne = section["NE"]
         
         # setting up state of simple or parent child question combination
         simple_questions = section["simple_questions"]
         parent_child_questions = section["parent_child_questions"]
         state = random.randint(0, len(simple_questions) - 1)
         no_s = simple_questions[state]
         no_pc = parent_child_questions[state]
         # state is the number of times the parent child question should have 3 child questions.


         total_questions = no_s + no_pc*2 + state
         difficulty_pool = self.prepare_difficulty_pool(total_questions)

         no_mcq_multiple = random.choice(mcq_multiple)
         no_ne = random.choice(ne)
         no_mcq_single = random.choice(mcq_single)
         no_ds = total_questions - (no_mcq_multiple + no_ne + no_mcq_single)

         prompt = ""
         qType = "simple"
         for i in range(no_ne):
            prompt = self.generate_prompt(difficulty_pool[i], "ne")
            section_prompts.append(prompt)
         for i in range(no_mcq_multiple):
            prompt = self.generate_prompt(difficulty_pool[i], "mcq_multiple")
            section_prompts.append(prompt)
         for i in range(no_ds):
            prompt = self.generate_prompt(difficulty_pool[i], "ds")
            section_prompts.append(prompt)
         no_s -= (no_ne + no_mcq_multiple + no_ds)  # numerical entry questions will always be simple type question
         
         if no_s < 0:
            state = (total_questions- (no_ne + no_mcq_multiple + no_ds))%2 
            no_pc = (total_questions- (no_ne + no_mcq_multiple + no_ds))//2
            no_s = 0
         remaining_questions = no_s + no_pc
         for i in range(remaining_questions):
            if no_s > 0:
               qType = "simple"
               no_s -= 1
            elif no_pc > 0:
               qType = "parent_child"
               if state > 0:
                  state -= 1
                  qType += "-3"
               else:
                  qType += "-2"
               no_pc -= 1

            prompt = self.generate_prompt(difficulty_pool[i], "mcq_single", qType)
            section_prompts.append(prompt)
         random.shuffle(section_prompts)
         all_prompts.append(section_prompts)

      return all_prompts

# q = Quants(mock_difficulty=1)
# sections = q.generate_question_prompts()
# for section in sections:
#     for prompt in section:
#         print(prompt)
#     print("-"*90)
