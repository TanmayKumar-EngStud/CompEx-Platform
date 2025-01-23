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
        initiator = max(1, self.combination_number)  # Ensure initiator is positive
        
        for key, values in self.combination.items():
            if key != "combination number":
                try:
                    if isinstance(values, list):
                        if not values:  # Skip empty lists
                            continue
                        length = len(values)
                    elif isinstance(values, int):
                        if values <= 0:  # Handle invalid integer values
                            values = 1
                        length = values
                    else:  # Skip invalid types
                        continue
                        
                    idx = initiator % length
                    
                    if isinstance(values, list):
                        if idx < len(values):  # Safety check for index
                            prompt += (f" - <{values[idx]}>")
                        else:
                            prompt += (f" - <{values[0]}>")  # Use first value as fallback
                    else:
                        prompt += (f" - <{idx+1}>")
                        
                    initiator = math.floor(initiator/length)
                except Exception as e:
                    print(f"Error processing {key}: {str(e)}")
                    continue  # Skip this item and continue with the next

        # Ensure we have at least one combination
        if not prompt:
            prompt = " - <1>"

        self.combination_number += 1
        self.combination["combination number"] = self.combination_number
        
        try:
            with open(os.path.join(os.path.dirname(__file__), "combination.json"), "w") as file:
                json.dump(self.combination, file, indent=4)
        except Exception as e:
            print(f"Error saving combination file: {str(e)}")
            
        return prompt
