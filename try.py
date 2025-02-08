import json

# Example raw string from the API
response_text = r"""
{
  "passage": "Alice invests a sum of money in a bank that offers a compound interest rate of 5% per annum. Bob invests the same amount in another bank that provides simple interest at the same rate for the same duration. After 3 years, the amount Alice has accumulated is $1050. What was the original amount invested by Alice and Bob? Additionally, how much total interest will Bob earn after the same period? The formulas for compound interest and simple interest are given by \( A = P(1 + r/n)^{nt} \) and \( A = P(1 + rt) \), respectively, where \( A \) is the amount, \( P \) is the principal, \( r \) is the rate, \( n \) is the number of times interest is compounded per year, and \( t \) is the time in years.",
  "statements": ["Alice's total investment after 3 years equals $1050.", "Bob's investment is made at simple interest with the same principal and duration."],
  "question": "Given the statements above, can we determine the original amount invested by both Alice and Bob?"
}
"""

# Function to refine the response
def refine_response(response_text):
    try:
        # Double escape backslashes
        json_str = response_text.replace("\\", "\\\\")

        # Parse the JSON string
        parsed = json.loads(json_str)

        # Return the JSON as a string
        return json.dumps(parsed)
    except json.JSONDecodeError as e:
        print(f"JSON validation error: {str(e)}\nJSON string:\n{json_str}\n")
        return None

# Example usage
refined_response = refine_response(response_text)
print("Refined Response:", refined_response)