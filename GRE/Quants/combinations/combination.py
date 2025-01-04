import json
import math
import os

class Combination:
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), "combination.json"), "r") as file:
            self.combination = json.load(file)
        self.combination_number = self.combination["combination number"]
    
    def pair_combination(self, length, combination_number):
        idx_1 = math.floor((combination_number - 1) / (length - 1))
        idx_2 = math.floor((combination_number - 1) % (length - 1))
        if idx_2 >= idx_1:
            idx_2 += 1
        return idx_1, idx_2 % length
    
    def generate_combination(self):
        prompt = []
        for section_name, details in self.combination.items():
            if section_name != "combination number":
                string = f"{section_name}"
                initiator = 1
                question_style_selected = ""
                filtered_topics = []

                for key, values in details.items():
                    if isinstance(values, list):
                        length = len(values)
                        idx = math.floor(self.combination_number / initiator)% length
                    elif isinstance(values, int):
                        idx = math.floor(self.combination_number / initiator)% values
                    if key == "questionStyle":
                        question_style_selected = values[idx]
                        string += (f" - <{values[idx]}>").replace("*", "").replace("$", "")
                        initiator *= length

                    elif key == "questionTopic":
                        if "Geometric Properties" in question_style_selected:
                            filtered_topics = [topic for topic in values if '*' in topic]
                        elif "Data Interpretation" in question_style_selected:
                            filtered_topics = [topic for topic in values if '$' in topic]
                        else:
                            filtered_topics = values
                        
                        length = len(filtered_topics)
                        idx = math.floor(self.combination_number / initiator) % length
                        string += (f" - <{filtered_topics[idx]}>").replace("*", "").replace("$", "")
                        initiator *= length

                    elif key == "tableType" and "Data Interpretation" in question_style_selected:
                        length = len(values)
                        idx = math.floor(self.combination_number / initiator) % length
                        string += (f" - <{values[idx]}>").replace("*", "").replace("$", "")
                        initiator *= length

                    elif key == "questionTheme" and "Word Problems" in question_style_selected:
                        idx_1, idx_2 = self.pair_combination(len(values), self.combination_number)
                        string += (f" - <{values[idx_1]}, {values[idx_2]}>").replace("*", "").replace("$", "")
                    else:
                        if isinstance(values, int):
                            string += (f" - <{idx+1}>").replace("*", "").replace("$", "")
                prompt.append(string)

        self.combination_number += 1
        self.combination["combination number"] = self.combination_number
        with open(os.path.join(os.path.dirname(__file__), "combination.json"), "w") as file:
            json.dump(self.combination, file, indent=4)
        return prompt
