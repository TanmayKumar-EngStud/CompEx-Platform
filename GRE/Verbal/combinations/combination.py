import json
import math
import os

class Combination:
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), "combination.json"), "r") as file:
            self.combination = json.load(file)
        self.combination_number = self.combination["combination number"]
    
    def pair_combination(self, length, combination_number):
        """
        Generate a pair of valid indices for the given length and combination number.
        Ensures indices are within bounds and not equal to each other.
        """
        if length < 2:
            return 0, 0  # Handle edge case of insufficient length
            
        # Ensure combination_number is positive
        combination_number = max(1, combination_number)
        
        # Calculate indices ensuring they're within bounds
        idx_1 = (combination_number - 1) % length
        idx_2 = ((combination_number - 1) // length) % length
        
        # Ensure indices are different
        if idx_1 == idx_2:
            idx_2 = (idx_2 + 1) % length
            
        return idx_1, idx_2
    
    def generate_combination(self):
        prompt = ""
        initiator = self.combination_number
        for key, values in self.combination.items():
            if key != "combination number":
                if isinstance(values, list):
                    length = len(values)
                elif isinstance(values, int):
                    length = values
                idx = initiator % length
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
