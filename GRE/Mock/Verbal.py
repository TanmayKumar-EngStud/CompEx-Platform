import json, os, random
class Verbal:
    def __init__(self, mock_difficulty):
        self.mock_difficulty = mock_difficulty
        self.total_questions = 27
        
        with open(os.path.join(os.path.dirname(__file__), "jsonfiles", "difficulty_distribution.json"), "r") as file:
            self.difficulty_distribution = json.load(file)["verbal"]

        with open(os.path.join(os.path.dirname(__file__), "jsonfiles", "component_allocation.json"), "r") as file:
            self.complete_component_allocation = json.load(file)
        self.component_allocation = self.complete_component_allocation["verbal"]
        self.combination_number = self.component_allocation["combination_number"]

        self.section_1 = self.component_allocation["section1"]
        self.section_2 = self.component_allocation["section2"]
        self.themes = self.component_allocation["themes"]
        self.rc_types = self.component_allocation["rc_types"]
        self.tc_types = self.component_allocation["tc_types"]
        self.se_types = self.component_allocation["se_types"]

    def generate_question_prompts(self) -> list[str]:

      # get difficulty ratio
      difficulty_ratio = self.difficulty_distribution[str(self.mock_difficulty)]
      easy_count = int(self.total_questions * difficulty_ratio["easy"])
      medium_count = int(self.total_questions * difficulty_ratio["medium"])
      hard_count = self.total_questions - (easy_count + medium_count)
    # we need to arrange the difficulty pool system here.
      one = random.randint(1, easy_count-1)
      three = random.randint(1, medium_count-1)
      five = random.randint(1, hard_count-1)
      two_three = random.randint(1, medium_count - three)
      two = easy_count - one + two_three
      four = hard_count - five + medium_count - three - two_three
      difficulty_pool = ([1]*one + [2]*two + [3]*three + [4]*four + [5]*five)
      random.shuffle(difficulty_pool)
      # shuffle the difficulty pool
      def generate_prompt(q_type, difficulty):
          questionTheme = self.themes[self.combination_number%len(self.themes)]
          vocab = str(random.randint(1,3)) if "tc" in q_type.lower() or "se" in q_type.lower() else ""
          self.combination_number += 1
          
          if self.combination_number%len(self.themes) == 0:
              random.shuffle(self.themes)

          self.component_allocation["combination_number"] = self.combination_number
          self.component_allocation["themes"] = self.themes

          with open(os.path.join(os.path.dirname(__file__), "jsonfiles", "component_allocation.json"), "w") as file:
              self.complete_component_allocation["verbal"] = self.component_allocation
              json.dump(self.complete_component_allocation, file)

          return f"<{questionTheme}> - <{q_type}> - <difficulty-level: {difficulty}> - <vocabulary-level:{vocab}>" if "rc" not in q_type.lower() else f"<{questionTheme}> - <{q_type}> - <difficulty-level: {difficulty}>"
      
      def allocate_questions(section_allocation):
          section_prompts = []
          num_rc = random.randint(*section_allocation["RC"])
          num_tc = random.randint(*section_allocation["TC"])
          num_se = 12 if section_allocation == self.section_1 else 15
          remaining_questions = num_se
          num_se -= (num_rc + num_tc)

          rc_combination = random.choice([["RC-S", "RC-L"], ["RC-M", "RC-M"], ["RC-L", "RC-M"]])
          num_rc_questions = 0
          for q_type in rc_combination[: num_rc]:
              section_prompts.append(generate_prompt(q_type, difficulty_pool.pop()))
              num_rc_questions += 2 if q_type == "RC-S" else 3 if q_type == "RC-M" else 4
          remaining_questions -= num_rc_questions

          tc_combination = ["TC-1", "TC-2", "TC-3"]
          if num_tc == 3:
              for tc in tc_combination[: num_tc]:
                  section_prompts.append(generate_prompt(tc, difficulty_pool.pop()))
          else:
              pin = random.randint(0, 2) # pinning system for TC question prompt generation
              itr = 0
              for tc in tc_combination[: num_tc]:
                  section_prompts.append(generate_prompt(tc, difficulty_pool.pop()))
                  if itr == pin:
                      section_prompts.append(generate_prompt(tc, difficulty_pool.pop()))
                  itr += 1
          for _ in range(num_se):
              section_prompts.append(generate_prompt("SE", difficulty_pool.pop()))
          return section_prompts
      
      section_1_prompts = allocate_questions(self.section_1)
      section_2_prompts = allocate_questions(self.section_2)

      
      return [section_1_prompts, section_2_prompts]

# v = Verbal(mock_difficulty=1)
# print(v.generate_question_prompts())