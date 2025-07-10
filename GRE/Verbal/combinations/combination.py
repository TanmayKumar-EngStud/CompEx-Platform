import json
import math
import os
import random

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
        # Use random number instead of persistent state
        self.original_combination_number = random.randint(1, 1000)
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

        prompt_components = []
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
                            prompt_components.append(values[idx])
                        else:
                            prompt_components.append(values[0])
                    else:
                        prompt_components.append(idx+1)
                        
                    initiator = math.floor(initiator/length)
                except Exception as e:
                    print(f"Error processing {key}: {str(e)}")
                    continue  # Skip this item and continue with the next

        # Ensure we have at least one combination
        if not prompt_components:
            prompt_components.append(1)

        # No persistent state - generate new random number for variety
        self.original_combination_number = random.randint(1, 1000)
        
        prompt = " - ".join(f"<{component}>" for component in prompt_components)

        return prompt
