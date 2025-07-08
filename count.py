import json
from collections import Counter

with open('public/words.json', 'r', encoding='utf-8') as f:
    data = json.load(f)  # data is a list of dicts

# Convert each dict to a tuple of sorted items, so hashable and unique
tupled = [tuple(sorted(d.items())) for d in data]

counter = Counter(tupled)
duplicates = [tup for tup, count in counter.items() if count > 1]

if not duplicates:
    print("No fully repeated lines found!")
else:
    print("Fully repeated lines (including all fields):")
    for tup in duplicates:
        # Convert tuple back to dict for pretty printing
        d = dict(tup)
        print(d)


# import json

# # Load JSON array
# with open('public/words.json', 'r', encoding='utf-8') as f:
#     data = json.load(f)

# seen = set()
# deduped = []
# for entry in data:
#     # Use tuple of sorted items for full unique match
#     tup = tuple(sorted(entry.items()))
#     if tup not in seen:
#         seen.add(tup)
#         deduped.append(entry)

# print(f"Deduplicated: {len(data) - len(deduped)} removed, {len(deduped)} kept.")

# # Overwrite file (or write to new file, e.g. 'words_deduped.json')
# with open('public/words.json', 'w', encoding='utf-8') as f:
#     json.dump(deduped, f, ensure_ascii=False, indent=2)