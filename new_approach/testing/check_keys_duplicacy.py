import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

api_keys = []
count = 0
while True:
    key = os.getenv(f"API_{count}")
    if not key:
        break
    api_keys.append(key)
    count += 1

print(f"Found {len(api_keys)} keys.")
unique_keys = set(api_keys)
print(f"Unique keys: {len(unique_keys)}")

if len(api_keys) != len(unique_keys):
    print("❌ WARNING: Duplicate keys detected!")
    # Find duplicates
    seen = set()
    dupes = []
    for i, k in enumerate(api_keys):
        if k in seen:
            dupes.append(f"API_{i}")
        seen.add(k)
    print(f"Duplicate indices: {dupes}")
else:
    print("✅ All keys are unique.")
