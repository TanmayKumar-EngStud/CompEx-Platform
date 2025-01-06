from files.questionComponents import ParentChildQuestion
import random, math, os, json
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
            prompts.append(f"{option[idx]}")
        child_prompt["combination number"] += 1
        json.dump(child_prompt, open(os.path.join(os.path.dirname(__file__), "../combinations/child-combination.json"), "w"))
        print(f"indexes: {indexes}")
        return prompts
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {}

    def generate_question(self):
        parentChildQuestion = ParentChildQuestion(self.llm, self.prompt)
        self.questionData["passages"] = parentChildQuestion.generate_passages()
        self.questionData["title"] = parentChildQuestion.generate_parentTitle()
        total_child_questions = 0
        if "rc-s" in self.prompt.lower():
            total_child_questions = 2
        elif "rc-m" in self.prompt.lower():
            total_child_questions = 3
        elif "rc-l" in self.prompt.lower():
            total_child_questions = 4
        
        child_prompts = self.generate_child_prompt(total_child_questions)
        print(f"child_prompts: {child_prompts}")
        self.questionData["childQuestions"] = []
        for i in range(total_child_questions):
            childQuestionData = {}
            childQuestionData["question"] = parentChildQuestion.generate_childQuestion(i, child_prompts[i])
            childQuestionData["options"] = parentChildQuestion.generate_childOptions(i)
            childQuestionData["solution"], childQuestionData["answer"] = parentChildQuestion.generate_childSolution(i)
            self.questionData["childQuestions"].append(childQuestionData)
        return self.questionData