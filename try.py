import json, re

response_text = "```json {'key'  : ['O'Reilly! '  , 'Python's Best',],} ```"

json_block_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
if json_block_match:
   json_str = json_block_match.group(1).strip()
else: 
   json_str = response_text

print(f"original: {json_str}")
# *,} -> *} ; *,] -> *]
json_str = re.sub(r',(\s*})', r'\1', json_str)
json_str = re.sub(r',(\s*])', r'\1', json_str)

print(f"level 1: {json_str}")
# {' -> {" ; [' -> [" ; '} -> "} ; '] -> "] ; '\s*: -> "\s*:
json_str = re.sub(r"(\[\s*)'", r'\1"', json_str)
json_str = re.sub(r"(\{\s*)'", r'\1"', json_str)
json_str = re.sub(r"'(\s*\])", r'"\1', json_str)
json_str = re.sub(r"'(\s*\})", r'"\1', json_str)
json_str = re.sub(r"'(\s*:)" , r'"\1', json_str)

print(f"level 2: {json_str}")

json_str = re.sub(r"([a-zA-Z0-9\s!.`]\s*)'(\s*,)", r'\1"\2', json_str)
json_str = re.sub(r"(,\s*)'(\s*[a-zA-Z0-9])", r'\1"\2', json_str)

print(f"level 3: {json_str}")

print(f"finally: \n{json.dumps(json_str)}")