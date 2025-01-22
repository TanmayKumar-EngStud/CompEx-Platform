from GMAT.Integrated_Reasoning.files.questionComponents import TPA
import random

class Generate_TPA:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
        self.questionData = {
            "thread_id": "",
            "part1": {
                "description": "",
                "graph": None,
                "table": None
            },
            "part2": {
                "description": "",
                "graph": None,
                "table": None
            },
            "question": "",
            "type": "No Math calculation",
            "title": "",
            "solution": "",
            "options": [],
            "answer": "",
            "tags": ["TPA"],
            "difficulty": 1
        }

    def generate_TPA(self):
        tpa = TPA(self.llm, self.prompt)
        
        # Generate question text and components
        thread_id, part1, part2, question, qtype = tpa.generate_QuestionText()
        self.questionData["thread_id"] = thread_id
        self.questionData["part1"] = part1
        self.questionData["part2"] = part2
        self.questionData["question"] = question or "Error generating question"
        self.questionData["type"] = qtype or "No Math calculation"
        
        # Generate title
        title = tpa.generate_QuestionTitle()
        self.questionData["title"] = title or "Two Part Analysis Question"
        
        # Generate options and answer
        options, answer = tpa.generate_QuestionOptions()
        if options and answer:
            option_list = list(options.values())
            random.shuffle(option_list)
            self.questionData["options"] = option_list
            self.questionData["answer"] = options[answer]
        else:
            self.questionData["options"] = ["Option A", "Option B", "Option C", "Option D"]
            self.questionData["answer"] = "Option A"
        
        # Generate solution
        solution = tpa.generate_QuestionSolution()
        self.questionData["solution"] = solution or "Solution not available"
        
        # Set tags and difficulty
        self.questionData["tags"] = ["TPA"]
        try:
            self.questionData["difficulty"] = int(self.prompt.split("-")[2].strip().strip('<>').strip())
        except:
            self.questionData["difficulty"] = 1
            
        return self.questionData