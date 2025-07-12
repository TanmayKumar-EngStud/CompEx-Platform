# ✅ verified, working fine, number of question prompts needed to be generated based on the section is working fine.
import json, os, random
class Verbal_prompts:
    def __init__(self, mock_difficulty):
        self.mock_difficulty = mock_difficulty
        self.total_questions = 27
        
        with open(os.path.join(os.path.dirname(__file__), "../../system_instructions/gre/difficulty_distribution.json"), "r") as file:
            self.difficulty_distribution = json.load(file)["verbal"]

        with open(os.path.join(os.path.dirname(__file__), "../../system_instructions/gre/customizations.json"), "r") as file:
            self.complete_customizations = json.load(file)
        self.customizations = self.complete_customizations["verbal"]
        self.combination_number = 0

        self.section_1 = self.customizations["section1"]
        self.section_2 = self.customizations["section2"]
        self.themes = self.customizations["questionTheme"]
        self.rc_types = self.customizations["reading_comprehension"]["question_types"]
        self.tc_types = self.customizations["text_completion"]["question_types"]
        self.se_types = self.customizations["sentence_equivalence"]["question_types"]

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
          # GRE Verbal nomenclature: "<questionType> - <questionTheme> - <focusedSkill> - <vocabulary_level: {1-3}> - <difficulty_level: {1-5}>"
          questionTheme = random.choice(self.themes)
          
          if "rc" in q_type.lower():
             # Reading Comprehension questions
             # rc-s = 1 child question, rc-m = 2 child questions, rc-l = 3 child questions
             if q_type == "rc-s":
                # 1 child question
                focused_skill = random.choice(self.customizations["child-question"]["focused_skill"])
             elif q_type == "rc-m":
                # 2 child questions - generate 2 separate focused skills
                focused_skills = random.sample(self.customizations["child-question"]["focused_skill"], 2)
                focused_skill = "/".join(focused_skills)
             else:  # rc-l
                # 3 child questions - generate 3 separate focused skills
                focused_skills = random.sample(self.customizations["child-question"]["focused_skill"], 3)
                focused_skill = "/".join(focused_skills)
             
             return f"<{q_type}> - <{questionTheme}> - <{focused_skill}> - <difficulty-level: {difficulty}>"
          else:
             # TC and SE questions - include vocabulary level
             vocab = str(random.randint(1,3))
             if "tc" in q_type.lower():
                 focused_skill = random.choice(self.customizations["text_completion"]["focused_skill"])
             else:  # SE question
                 focused_skill = random.choice(self.customizations["sentence_equivalence"]["focused_skill"])
             return f"<{q_type}> - <{questionTheme}> - <{focused_skill}> - <vocabulary-level: {vocab}> - <difficulty-level: {difficulty}>"
      
      def allocate_questions(section_allocation):
          section_prompts = []
          
          # GRE RC sections need exactly 10 child questions
          # rc-s = 2 child questions, rc-m = 3 child questions, rc-l = 4 child questions
          # Generate combinations that total exactly 10 child questions
          rc_combinations = self.customizations["reading_comprehension"]["combinations"]
          
          rc_combination = random.choice(rc_combinations)
          
          # Calculate actual child questions to verify
          num_rc = sum(2 if _ == "rc-s" else 3 if _ == "rc-m" else 4 for _ in rc_combination)
          
          # Get TC and SE counts from section allocation
          num_tc = section_allocation["TC"][0]  # Should be 6 for both sections
          num_se = section_allocation["SE"][0]  # Should be 4 for both sections
          # Generate RC prompts
          for q_type in rc_combination:
              section_prompts.append(generate_prompt(q_type, difficulty_pool.pop()))

          # Generate TC prompts
          tc_types = [tc.upper() for tc in self.customizations["text_completion"]["question_types"]]
          for _ in range(num_tc):
              tc_type = random.choice(tc_types)
              section_prompts.append(generate_prompt(tc_type, difficulty_pool.pop()))
          
          # Generate SE prompts
          for _ in range(num_se):
              se_type = self.customizations["sentence_equivalence"]["question_types"][0].upper()
              section_prompts.append(generate_prompt(se_type, difficulty_pool.pop()))
          return section_prompts
      
      section_1_prompts = allocate_questions(self.section_1)
      section_2_prompts = allocate_questions(self.section_2)
      random.shuffle(section_1_prompts)
      random.shuffle(section_2_prompts)
      
      return [section_1_prompts, section_2_prompts]

# v = Verbal(mock_difficulty=1)
# sections = v.generate_question_prompts()
# for section in sections:
#     for prompt in section:
#         print(prompt)
#     print("-"*90)