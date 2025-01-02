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
        prompt = ""
        initiator = self.combination_number
        for key, values in self.combination.items():
            if key != "combination number":
                if isinstance(values, list):
                    length = len(values)
                elif isinstance(values, int):
                    length = values
                idx =initiator % length
                if isinstance(values, list):
                    prompt += (f" - <{values[idx]}>")
                else:
                    prompt += (f" - <{idx+1}>")
                initiator = math.floor(initiator/length)

        self.combination_number += 1
        self.combination["combination number"] = self.combination_number
        with open(os.path.join(os.path.dirname(__file__), "combination.json"), "w") as file:
            json.dump(self.combination, file, indent=4)
        return prompt
