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
        self.original_combination_number = self.combination["combination number"]
        total_number_of_combinations = self.find_total_number_of_combinations()
        self.combination_number = binary_search_instance(self.original_combination_number, total_number_of_combinations)
    
    def find_total_number_of_combinations(self):
        total_number_of_combinations = 1
        for component, value in self.combination.items():
            if component != "combination number":
                if isinstance(value, list):
                    total_number_of_combinations *= len(value)
                elif isinstance(value, int):
                    total_number_of_combinations *= value
        return total_number_of_combinations
    
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
        prompt = []
        for section_name, details in self.combination.items():
            if section_name != "combination number":
                string = f"{section_name}"
                initiator = 1
                question_style_selected = ""
                filtered_topics = []

                for key, values in details.items():
                    # Skip if values is None or empty
                    if not values:
                        continue
                        
                    if isinstance(values, list):
                        length = len(values)
                        if length == 0:  # Skip if list is empty
                            continue
                        idx = math.floor(self.combination_number / initiator) % length
                    elif isinstance(values, int):
                        if values <= 0:  # Handle invalid integer values
                            values = 1
                        idx = math.floor(self.combination_number / initiator) % values
                        
                    if key == "questionStyle":
                        question_style_selected = values[idx] if idx < len(values) else values[0]
                        string += (f" - <{values[idx]}>").replace("*", "").replace("$", "")
                        initiator *= length

                    elif key == "questionTopic":
                        if "Geometric Properties" in question_style_selected:
                            filtered_topics = [topic for topic in values if '*' in topic]
                        elif "Data Interpretation" in question_style_selected:
                            filtered_topics = [topic for topic in values if '$' in topic]
                        else:
                            filtered_topics = values
                        
                        if not filtered_topics:  # If no topics match the filter, use all topics
                            filtered_topics = values
                            
                        length = len(filtered_topics)
                        if length > 0:  # Only proceed if we have topics
                            idx = math.floor(self.combination_number / initiator) % length
                            string += (f" - <{filtered_topics[idx]}>").replace("*", "").replace("$", "")
                            initiator *= length

                    elif key == "tableType" and "Data Interpretation" in question_style_selected:
                        if isinstance(values, list) and len(values) > 0:
                            length = len(values)
                            idx = math.floor(self.combination_number / initiator) % length
                            string += (f" - <{values[idx]}>").replace("*", "").replace("$", "")
                            initiator *= length

                    elif key == "questionTheme" and "Word Problems" in question_style_selected:
                        if isinstance(values, list) and len(values) > 0:
                            idx_1, idx_2 = self.pair_combination(len(values), self.combination_number)
                            string += (f" - <{values[idx_1]}, {values[idx_2]}>").replace("*", "").replace("$", "")
                    else:
                        if isinstance(values, int):
                            string += (f" - <{idx+1}>").replace("*", "").replace("$", "")
                prompt.append(string)

        self.original_combination_number += 1
        self.combination["combination number"] = self.original_combination_number
        with open(os.path.join(os.path.dirname(__file__), "combination.json"), "w") as file:
            json.dump(self.combination, file, indent=4)
        return prompt
