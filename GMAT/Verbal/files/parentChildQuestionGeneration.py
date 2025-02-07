import random, math,os, json, re
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from dotenv import load_dotenv
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable

from Verbal.files.questionComponents import ParentChildQuestion
class ParentChildQuestionGeneration:
    def generate_child_prompt(self, idx):
        child_prompt = json.load(open(os.path.join(os.path.dirname(__file__), "../combinations/child-combination.json"), "r"))
        prompts = []
        t = int(child_prompt["combination number"])
        indexes = []
        for i in range(idx):
            option = child_prompt["reading comprehension"]
            idx = t%len(option)
            counter = 0
            for j in indexes:
                if j <= idx+counter:
                    counter += 1
            indexes.append((idx+counter)%len(option))
            t = t//len(option)
            difficulty = random.randint(1, 5)
            prompts.append(f"{option[idx]} - <{difficulty}>")
        child_prompt["combination number"] += 1

        if (t+1)%len(child_prompt["reading comprehension"]) == 0:
            random.shuffle(child_prompt["reading comprehension"])
    
        json.dump(child_prompt, open(os.path.join(os.path.dirname(__file__), "../combinations/child-combination.json"), "w"))
        
        return prompts
    def __init__(self, prompt=None):
        load_dotenv()
        assistant_id = json.load(open(os.path.join(os.path.dirname(__file__), "../../assistant_ids.json"), "r"))["GMAT-Verbal-Parent-Child-Questions"]

        llm = OpenAIAssistantRunnable(
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
                assistant_id=assistant_id
        )
        self.llm = llm
        self.prompt = prompt
        child_question_numbers = 0
        if "rc_3" in self.prompt.lower():
            child_question_numbers = 3
        elif "rc_4" in self.prompt.lower():
            child_question_numbers = 4
        self.number_of_child_questions = child_question_numbers
        self.child_prompt = self.generate_child_prompt(child_question_numbers)
        self.questionData = {}
    def generate_question(self):
        self.questionData["type"] = "RC"
        self.questionData["prompt"] = self.prompt
        questionContent = ParentChildQuestion(self.llm, self.prompt, self.number_of_child_questions)
        self.questionData["thread_id"], passages = questionContent.generate_parentPassage()
        self.questionData["content"] = {"passages": passages}
        self.questionData["title"] = questionContent.generate_parentTitle()
        self.questionData["childQuestions"] = []
        self.questionData["tags"] = []
        child_question_numbers = len(self.child_prompt) if self.child_prompt else random.randint(2, 4)
        for i in range(child_question_numbers):
            childQuestionData = {}
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
            self.questionData["childQuestions"].append(childQuestionData)
        return self.questionData