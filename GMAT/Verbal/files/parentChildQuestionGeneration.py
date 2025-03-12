import random, os, json, re
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from dotenv import load_dotenv
from google import genai
# GMAT.Verbal.files.
from GMAT.Verbal.files.questionComponents import ParentChildQuestion
class ParentChildQuestionGeneration:
    def generate_child_prompt(self, idx, difficulty):
        child_prompt = json.load(open(os.path.join(os.path.dirname(__file__), "../combinations/child-combination.json"), "r"))
        prompts = []
        t = int(child_prompt["combination number"])
        indexes = []
        for _ in range(idx):
            option = child_prompt["reading comprehension"]
            idx = t%len(option)
            counter = 0
            for j in indexes:
                if j <= idx+counter:
                    counter += 1
            indexes.append((idx+counter)%len(option))
            t = t//len(option)
            
            #region setting appropriate difficulty level:
            diff =  difficulty + random.randint(-1,1)
            if diff < 1:
                diff = 1
            if diff > 5:
                diff = 5
            #endregion

            prompts.append(f"{option[idx]} - <difficulty_level: {diff}>")
        child_prompt["combination number"] += 1

        if (t+1)%len(child_prompt["reading comprehension"]) == 0:
            random.shuffle(child_prompt["reading comprehension"])
    
        json.dump(child_prompt, open(os.path.join(os.path.dirname(__file__), "../combinations/child-combination.json"), "w"))
        
        return prompts

    def __init__(self, global_state, lock, api_IDX, prompt):
        load_dotenv()
        self.global_state = global_state
        self.lock = lock
        api_key = os.getenv(f"API_{api_IDX}")
        llm = genai.Client(api_key = api_key)
        self.llm = llm
        self.prompt = prompt
        child_question_numbers = 0
        if "rc_3" in self.prompt.lower():
            child_question_numbers = 3
        elif "rc_4" in self.prompt.lower():
            child_question_numbers = 4
        self.number_of_child_questions = child_question_numbers
        difficulty = re.search(r'<difficulty_level: (\d+)>', self.prompt)
        if difficulty:
            difficulty= int(difficulty.group(1))
        else:
            difficulty = 0
        self.child_prompt = self.generate_child_prompt(child_question_numbers, difficulty)
        self.questionData = {}
        with open(os.path.join(os.path.dirname(__file__), "../System_instructions/GMAT-Verbal-Parent-Child-Questions.txt"), "r") as f:
            self.system_instructions = f.read()

    def generate_question(self):
        self.questionData["type"] = "RC"
        self.questionData["prompt"] = self.prompt
        questionContent = ParentChildQuestion(self.llm, self.system_instructions, self.global_state, self.prompt, self.lock, self.number_of_child_questions)
        passages = questionContent.generate_parentPassage()
        self.questionData["content"] = {"passages": passages}

        difficulty = re.search(r'<difficulty_level: (\d+)>', self.prompt)
        if difficulty:
            difficulty= int(difficulty.group(1))
        else:
            difficulty = 0

        self.questionData["title"] = questionContent.generate_parentTitle()
        self.questionData["difficulty"] = difficulty

        self.questionData["questions"] = []
        self.questionData["tags"] = []
        child_question_numbers = len(self.child_prompt) if self.child_prompt else random.randint(2, 4)
        for i in range(child_question_numbers):
            childQuestionData = {}
            childQuestionData["prompt"] = self.child_prompt[i]
            childQuestionData["question"] = questionContent.generate_childQuestion(i, self.child_prompt[i] if self.child_prompt else "")
            childQuestionData["title"] = questionContent.generate_childQuestionTitle(i)
            options, answer= questionContent.generate_childOptions(i)
            childQuestionData["answer"] = options[answer]
            options_list = list(options.values())
            random.shuffle(options_list)
            childQuestionData["options"] = options_list
            childQuestionData["solution"] = questionContent.generate_childSolution(i)
            pattern = r'<difficulty_level: (\d+)>'
            difficulty = re.search(pattern, self.child_prompt[i])
            if difficulty:
               childQuestionData["difficulty"] = int(difficulty.group(1))
            else:
               childQuestionData["difficulty"] = -1
            childQuestionData["tags"] = [self.child_prompt[i].split("-")[0].strip().strip()]
            self.questionData["tags"].extend(childQuestionData["tags"])
            self.questionData["questions"].append(childQuestionData)

        return self.questionData