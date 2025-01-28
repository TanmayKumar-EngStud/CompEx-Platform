import json
import math
import os

def binary_search_instance(x: int, y: int) -> int:
    x %= y 

    low, high = 1, y
    mid = (low + high) // 2
    for i in range(1, x + 1):
        mid = (low + high) // 2
        if mid < x:
            low = mid + 1
        else:
            high = mid - 1
    return mid
class Combination:
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), "combination.json"), "r") as file:
            self.combination = json.load(file)
        self.combination_number = self.combination["combination number"]
    
    def pair_combination(self, length, combination_number):
        """Generate two unique indices for pairing values.
        Args:
            length: Length of the values list
            combination_number: Current combination number
        Returns:
            Tuple of two indices that are within bounds and different from each other
        """
        if length < 2:
            return 0, 0
            
        # Ensure combination_number is positive
        combination_number = max(1, combination_number)
        
        # Calculate total possible combinations
        total_combinations = length * (length - 1)
        
        # Use modulo to wrap around
        adjusted_number = ((combination_number - 1) % total_combinations) + 1
        
        # Calculate indices ensuring they're different and within bounds
        idx_1 = ((adjusted_number - 1) // (length - 1)) % length
        idx_2 = ((adjusted_number - 1) % (length - 1))
        
        # Adjust second index if it's equal to or greater than first index
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
