# GRE.Verbal.files.
from Verbal.files.questionComponents import ParentChildQuestion
import random, math, os, json
from dotenv import load_dotenv
from google import genai

class ParentChildQuestionGeneration:
    def generate_child_prompt(self, idx):
        child_prompt = json.load(open(os.path.join(os.path.dirname(__file__), "../combinations/child-combination.json"), "r"))
        prompts = []
        t = child_prompt["combination number"]
        indexes = []
        for i in range(idx):
            option = child_prompt["reading comprehension"]
            idx = t%len(option)
            counter = 0
            for j in indexes:
                if j <= idx+counter:
                    counter += 1
            indexes.append((idx+counter)%len(option))
            t = math.floor(t/len(option))
            difficulty = random.randint(1, 5)
            prompts.append(f"{option[idx]} - {difficulty}")
        child_prompt["combination number"] += 1
        json.dump(child_prompt, open(os.path.join(os.path.dirname(__file__), "../combinations/child-combination.json"), "w"))
        # print(f"indexes: {indexes}")
        return prompts
    def __init__(self, global_state, lock, api_IDX, prompt):
        load_dotenv()
        self.global_state = global_state
        self.lock = lock
        api_key = os.getenv(f"API_{api_IDX}")
        llm = genai.Client(api_key = api_key)
        with open(os.path.join(os.path.dirname(__file__), "../System_instructions/GRE-Verbal-Parent-Child-Questions.txt"), "r") as f:
            self.system_instructions = f.read()
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}

    def shuffle_options(self,options):
        option_list = []
        if isinstance(options, dict):
            # Shuffle the values of the dictionary
            option_list = list(options.values())
            random.shuffle(option_list)
        elif isinstance(options, list):
            # Shuffle values of each inner dictionary and convert to list of lists
            for inner_dict in options:
                shuffled_values = list(inner_dict.values())
                random.shuffle(shuffled_values)
                option_list.append(shuffled_values)
        return option_list

    def generate_question(self):
        parentChildQuestion = ParentChildQuestion(self.llm, self.system_instructions, self.global_state, self.prompt, self.lock)
        self.questionData["type"] = "RC"
        self.questionData["prompt"] = self.prompt
        passages= parentChildQuestion.generate_passages()
        self.questionData["content"] = {"passages": passages}
        self.questionData["title"] = parentChildQuestion.generate_parentTitle()
        total_child_questions = 0
        if "rc-s" in self.prompt.lower():
            total_child_questions = 2
            self.questionData["tags"]= ["rc-s"]
        elif "rc-m" in self.prompt.lower():
            total_child_questions = 3
            self.questionData["tags"]= ["rc-m"]
        elif "rc-l" in self.prompt.lower():
            total_child_questions = 4
            self.questionData["tags"]= ["rc-l"]
        
        child_prompts = self.generate_child_prompt(total_child_questions)

        # print(f"child_prompts: {child_prompts}")
        self.questionData["questions"] = []
        for i in range(total_child_questions):
            childQuestionData = {}
            childQuestionData["type"] = "RC"
            childQuestionData["prompt"] = child_prompts[i]
            childQuestionData["question"] = parentChildQuestion.generate_childQuestion(i, child_prompts[i])
            childQuestionData["title"] = parentChildQuestion.generate_childQuestionTitle(i)
            options, answer = parentChildQuestion.generate_childOptions(i)
            if(isinstance(answer, str)):
                childQuestionData["answer"] = options[answer]
            else:
                answers = []
                i=0
                for ans in answer:
                    answers.append(options[i][ans])
                    i+=1
                childQuestionData["answer"] = answers
            childQuestionData["options"] = self.shuffle_options(options)
            childQuestionData["solution"] = parentChildQuestion.generate_childSolution(i)

            childQuestionData["tags"] = [child_prompts[i].split("-")[0]]
            childQuestionData["difficulty"] = int(child_prompts[i].split("-")[1].strip())
            # print(f"this is childQuestionData: \n{childQuestionData}\n\n")
            self.questionData["tags"].extend(childQuestionData["tags"])
            self.questionData["questions"].append(childQuestionData)
        
        return self.questionData