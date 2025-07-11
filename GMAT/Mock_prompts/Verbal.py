#
import json
import os
import random


class Verbal_prompts:
    def __init__(self, mock_difficulty):
        self.mock_difficulty = mock_difficulty
        self.total_questions = 23

        with open(os.path.join(os.path.dirname(__file__), "../../system_instructions/gmat/difficulty_distribution.json"), "r") as file:
            self.difficulty_distribution = json.load(file)["verbal"]

        with open(os.path.join(os.path.dirname(__file__), "../../system_instructions/gmat/customizations.json"), "r") as file:
            self.complete_customizations = json.load(file)
            self.customizations = self.complete_customizations["verbal"]
        self.combination_number = 0
        self.themes = self.customizations["themes"]
        self.cr_types = self.customizations["child-question"]["focused_skill"]

    def get_difficulty_pool(self) -> list[int]:
        difficulty_ratio = self.difficulty_distribution[str(
            self.mock_difficulty)]
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

        # Select RC/CR distribution randomly
        itr = random.randint(0, 1)
        num_rc_questions = self.customizations["section"]["RC"][itr]
        num_cr_questions = self.customizations["section"]["CR"][itr]

        # Generate RC questions
        rcs = []
        if num_rc_questions == 13:
            # 13 child questions: 3+3+3+2+2+3 = 16 total but we use 13
            rcs = ["rc-s", "rc-s", "rc-s", "rc-m", "rc-m", "rc-l"]
        else:
            # 14 child questions: 3+3+2+2+3+3 = 16 total but we use 14
            rcs = ["rc-s", "rc-s", "rc-m", "rc-m", "rc-l", "rc-l"]

        # Generate RC prompts
        for rc in rcs:
            # Reading Comprehension nomenclature: "<questionType> - <questionTheme> - <focused_skill{i}/focused_skill{i+1}> - <vocabulary_level: {1-3}> - <difficulty_level: {1-5}>"
            # rc-s will have 1 child question, rc-m will have 2 and rc-l => 3, so we will be having focused skills captured just like that
            theme = random.choice(self.themes)
            vocabulary_level = random.randint(1, 3)

            # Generate focused skills based on question type
            if rc == "rc-s":
                focused_skill = random.choice(
                    self.customizations["child-question"]["focused_skill"])
                focused_skills_str = focused_skill
            elif rc == "rc-m":
                focused_skills = random.sample(
                    self.customizations["child-question"]["focused_skill"], 2)
                focused_skills_str = "/".join(focused_skills)
            else:  # rc-l
                focused_skills = random.sample(
                    self.customizations["child-question"]["focused_skill"], 3)
                focused_skills_str = "/".join(focused_skills)

            prompt = f"<{rc}> - <{theme}> - <{focused_skills_str}> - <vocabulary_level: {vocabulary_level}> - <difficulty_level: {difficulty_pool.pop()}>"
            prompts.append(prompt)

        # Generate CR questions
        for cr in range(num_cr_questions):
            # Critical Reasoning nomenclature: "<questionType> - <questionTheme> - <focused_skill> - <vocabulary_level: {1-3}> - <difficulty_level: {1-5}>"
            # for normal critical reasoning use focused_skill lists from the "child-question" key
            theme = random.choice(self.themes)
            cr_type = random.choice(self.cr_types)
            vocabulary_level = random.randint(1, 3)

            prompt = f"<CR> - <{theme}> - <{cr_type}> - <vocabulary_level: {vocabulary_level}> - <difficulty_level: {difficulty_pool.pop()}>"
            prompts.append(prompt)

        random.shuffle(prompts)
        return prompts

# v = Verbal(1)
# prompts = v.generate_question_prompts()
# for prompt in prompts:
#    print(prompt)
# print(f"length of prompts: {len(prompts)}")
