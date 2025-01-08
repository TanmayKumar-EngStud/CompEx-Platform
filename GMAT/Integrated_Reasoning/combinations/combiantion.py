import json
import math
import os
class Combination:
   def __init__(self):
      with open(os.path.join(os.path.dirname(__file__), "combination.json"), "r") as file:
         self.combination = json.load(file)
      self.combination_number = self.combination["combination number"]
   
   def pair_combination(self, length, combination_number):
      idx_1 = math.floor(combination_number-1/length-1)%length
      idx_2 = math.floor(combination_number-1%(length-1))
      if(idx_2 >= idx_1):
         idx_2 += 1
      return idx_1, idx_2%length
   
   def generate_combination(self):
      prompt = []
      for section_name, details in self.combination.items():
         if(section_name != "combination number"):
            string = f"{section_name}"
            initiator = 1
            for key, value in details.items():
               length = len(value) if isinstance(value, list) else value
               idx = math.floor(self.combination_number/initiator)%length
               if(isinstance(value, int)):
                  string += f" - <{idx+1}>"
               elif(key == "questionTheme"):
                  idx_1, idx_2 = self.pair_combination(length, idx+1)
                  string += f" - <{value[idx_1]}, {value[idx_2]}>"
               else:
                  string += f" - <{value[idx]}>"
            
            prompt.append(string)
      self.combination_number += 1
      self.combination["combination number"] = self.combination_number
      with open(os.path.join(os.path.dirname(__file__), "combination.json"), "w") as file:
         json.dump(self.combination, file, indent=4)
      return prompt