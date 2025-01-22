import random, math,os, json

from GMAT.Verbal.files.questionComponents import ParentChildQuestion
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
            prompts.append(f"{option[idx]} - <{difficulty}>")
        child_prompt["combination number"] += 1
        json.dump(child_prompt, open(os.path.join(os.path.dirname(__file__), "../combinations/child-combination.json"), "w"))
        
        return prompts
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        child_question_numbers = 0
        if "rc-s" in self.prompt.lower():
            child_question_numbers = 2
        elif "rc-m" in self.prompt.lower():
            child_question_numbers = 3
        elif "rc-l" in self.prompt.lower():
            child_question_numbers = 4
        self.child_prompt = self.generate_child_prompt(child_question_numbers)
        self.questionData = {}
    def generate_question(self):
        questionContent = ParentChildQuestion(self.llm, self.prompt)
        self.questionData["thread_id"], self.questionData["passage"] = questionContent.generate_parentPassage()
        self.questionData["title"] = questionContent.generate_parentTitle()
        self.questionData["childQuestions"] = []
        self.questionData["tags"] = [self.prompt.split(" - ")[2].strip().strip('<>').strip()] 
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
            childQuestionData["difficulty"] = int(self.child_prompt[i].split("-")[1].strip().strip('<>').strip())
            childQuestionData["tags"] = [self.child_prompt[i].split("-")[0].strip().strip()]
            self.questionData["tags"].extend(childQuestionData["tags"])
            self.questionData["childQuestions"].append(childQuestionData)
        return self.questionData