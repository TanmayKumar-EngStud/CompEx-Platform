import re

tag = re.sub(r'\([^)]*\)', '', "I love my India (and also Pakistan)")

print(tag)