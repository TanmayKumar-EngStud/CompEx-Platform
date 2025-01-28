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
   
   def find_total_number_of_combinations(self):
      total_number_of_combinations = 1
      for component, value in self.combination.items():
         if component != "combination number":
            if isinstance(value, list):
               total_number_of_combinations *= len(value)
            elif isinstance(value, int):
               total_number_of_combinations *= value
      return total_number_of_combinations

   def generate_combination(self):
      prompt = []
      for section_name, details in self.combination.items():
         if section_name != "combination number":
            try:
               string = f"{section_name}"
               initiator = 1
               
               for key, value in details.items():
                  # Skip if value is None or empty
                  if not value:
                     continue
                     
                  if isinstance(value, list):
                     if not value:  # Skip empty lists
                        continue
                     length = len(value)
                  elif isinstance(value, int):
                     if value <= 0:  # Handle invalid integer values
                        value = 1
                     length = value
                  else:  # Skip invalid types
                     continue
                     
                  idx = math.floor(self.combination_number/initiator) % length
                  
                  if isinstance(value, int):
                     string += f" - <{idx+1}>"
                  elif key == "questionTheme":
                     if length >= 2:  # Only generate pairs if we have at least 2 items
                        idx_1, idx_2 = self.pair_combination(length, idx+1)
                        string += f" - <{value[idx_1]}, {value[idx_2]}>"
                     else:
                        string += f" - <{value[0]}>"  # Use single value if not enough items
                  else:
                     if idx < len(value):  # Safety check for index
                        string += f" - <{value[idx]}>"
                     else:
                        string += f" - <{value[0]}>"  # Use first value as fallback
                        
                  initiator *= length
                  
               prompt.append(string)
            except Exception as e:
               print(f"Error processing section {section_name}: {str(e)}")
               continue  # Skip this section and continue with the next

      # Ensure we have at least one combination
      if not prompt:
         prompt = ["Section - <1>"]

      self.original_combination_number += 1
      self.combination["combination number"] = self.original_combination_number
      
      try:
         with open(os.path.join(os.path.dirname(__file__), "combination.json"), "w") as file:
            json.dump(self.combination, file, indent=4)
      except Exception as e:
         print(f"Error saving combination file: {str(e)}")
         
      return prompt