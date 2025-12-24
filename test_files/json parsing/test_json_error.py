import json

data_str = '''
{
  "options": {
    "A": {
      "text": "Quantity A is greater.",
      "explanation": "**Incorrect** because \( C(8,3) = C(8,5) \) makes them equal."
    },
    "B": {
      "text": "Quantity B is greater.",
      "explanation": "**Incorrect** as the symmetry of combinations ensures equality."
    },
    "C": {
      "text": "The two quantities are equal.",
      "explanation": "**Correct** since \( C(8,3) = C(8,5) \) by the property \( C(n,r) = C(n,n-r) \)."
    },
    "D": {
      "text": "The relationship cannot be determined from the information given.",
      "explanation": "**Incorrect** because the information suffices to calculate and compare the quantities."
    }
  },
  "answer": "C"
}
'''

try:
    json.loads(data_str)
    print("Success")
except json.JSONDecodeError as e:
    print(f"Failed: {e}")
