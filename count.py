import json

with open('public/words.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Number of entries: {len(data)}")
