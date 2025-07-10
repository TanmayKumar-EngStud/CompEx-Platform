import json
import os
import random

def binary_search_instance(x: int, y: int) -> int:
    x %= y 
    low, high = 1, y
    mid = (low + high) // 2
    for _ in range(1, x + 1):
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
      #   print(f"combination number found: {self.combination_number}")

    def find_total_number_of_combinations(self):
        total_number_of_combinations = 1
        for component, value in self.combination.items():
            if component != "combination number":
                if isinstance(value, dict):
                    for key, sub_value in value.items():
                        if isinstance(sub_value, list):
                            total_number_of_combinations *= len(sub_value)
                        elif isinstance(sub_value, int):
                            total_number_of_combinations *= sub_value
        return total_number_of_combinations
    
    def generate_combination(self):
        prompt = []
        for section_name, details in self.combination.items():
            if section_name != 'combination number':
                prompt_items = [section_name]
                initiator = 1
                Type = None
                selectors =  ["*", "&", "$"]
                for property, values in details.items():
 
                  if isinstance(values, int):
                     values = max(1, values)
                     idx = (self.combination_number//initiator) % values
                     prompt_items.append(f"<{idx+1}>")
                     initiator *= values
                  elif isinstance(values, list):
                     if not Type:
                         idx = (self.combination_number//initiator) % len(values)
                         selected_item = values[idx]
                         if selected_item:
                           initiator *= len(values)
                           for selector in selectors:
                              if selector in selected_item:
                                    Type = selector
                           selected_item = str(selected_item).replace('*', '').replace('&', '').replace('$', '')
                           prompt_items.append(f"<{selected_item}>")

                     else: 
                         execute = True
                         for selector in selectors:
                             if selector in property:
                                 execute = False
                                 # if the selector is present in the properties and Type is equal to properties then only add the component else skip it
                                 if Type == selector:
                                     idx = (self.combination_number // initiator) % len(values)
                                     selected_item = values[idx]
                                     if selected_item:
                                       initiator *= len(values)
                                       prompt_items.append(f"<{selected_item}>")
                                 break
                         if execute:
                           validate = False
                           for val in values:
                              if not val:
                                 continue
                              if Type in val:
                                    validate = True
                                    break
                           if validate:
                              filtered_values = [value for value in values if Type in value]
                              idx = (self.combination_number // initiator ) % len(filtered_values)
                              selected_item = filtered_values[idx]
                              if selected_item:
                                 initiator *= len(filtered_values)
                                 prompt_items.append(f"<{selected_item.replace(Type, '')}>")
                           else:
                              filtered_values =[]
                              for value in values:
                                  if not value:
                                      continue
                                  add = True
                                  for selector in selectors:
                                      if selector in value and selector != Type:
                                          add = False
                                  if add:
                                      filtered_values.append(value)
                              
                              idx = (self.combination_number // initiator) % len(filtered_values)
                              selected_item = filtered_values[idx]
                              if selected_item:
                                 initiator *= len(filtered_values)
                                 prompt_items.append(f"<{str(selected_item).replace(Type, '')}>") 

                prompt.append(" - ".join(prompt_items))
        
        # No persistent state - generate new random number for variety
        self.original_combination_number = random.randint(1, 1000)
        return prompt
