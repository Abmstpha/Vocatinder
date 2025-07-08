#!/usr/bin/env python3
"""
Detailed analysis of duplicate words in the French Gender Swipe JSON file.
Shows the full context of each duplicate word including gender and translation.
"""

import json
from collections import defaultdict

def detailed_duplicate_analysis():
    """Provide detailed analysis of duplicate words with their full context."""
    
    # Load the JSON data
    with open('public/words.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Group entries by word
    word_groups = defaultdict(list)
    for i, entry in enumerate(data):
        word_groups[entry['word']].append((i, entry))
    
    # Find duplicates
    duplicates = {word: entries for word, entries in word_groups.items() if len(entries) > 1}
    
    print("🔍 Detailed Analysis of Duplicate Words in public/words.json")
    print("=" * 70)
    print(f"Total entries: {len(data)}")
    print(f"Duplicate words found: {len(duplicates)}")
    print()
    
    # Sort duplicates by frequency (descending) and then alphabetically
    sorted_duplicates = sorted(duplicates.items(), key=lambda x: (-len(x[1]), x[0]))
    
    print("📊 Detailed breakdown of each duplicate word:")
    print("-" * 70)
    
    for word, entries in sorted_duplicates:
        print(f"\n🔤 '{word}' appears {len(entries)} times:")
        
        # Check if all entries are identical
        first_entry = entries[0][1]
        all_identical = all(entry == first_entry for _, entry in entries)
        
        if all_identical:
            print(f"   ✅ All entries identical: {first_entry}")
            print(f"   📍 Found at positions: {[pos for pos, _ in entries]}")
        else:
            print(f"   ⚠️  Entries have differences:")
            for pos, entry in entries:
                print(f"      Position {pos}: {entry}")
    
    # Additional analysis
    print("\n" + "=" * 70)
    print("📈 Summary Statistics:")
    
    # Count how many words appear exactly 2, 3, 4, etc. times
    frequency_counts = defaultdict(int)
    for word, entries in duplicates.items():
        frequency_counts[len(entries)] += 1
    
    print(f"   - Words appearing exactly 2 times: {frequency_counts[2]}")
    print(f"   - Words appearing exactly 3 times: {frequency_counts[3]}")
    print(f"   - Words appearing exactly 4 times: {frequency_counts[4]}")
    print(f"   - Words appearing 5 or more times: {sum(count for freq, count in frequency_counts.items() if freq >= 5)}")
    
    # Find the most duplicated word
    max_duplicated = max(duplicates.items(), key=lambda x: len(x[1]))
    print(f"   - Most duplicated word: '{max_duplicated[0]}' ({len(max_duplicated[1])} times)")
    
    # Check for inconsistencies in gender/translation
    inconsistent_words = []
    for word, entries in duplicates.items():
        first_entry = entries[0][1]
        for _, entry in entries[1:]:
            if entry['gender'] != first_entry['gender'] or entry['translation'] != first_entry['translation']:
                inconsistent_words.append(word)
                break
    
    if inconsistent_words:
        print(f"\n⚠️  Words with inconsistent gender/translation:")
        for word in inconsistent_words:
            print(f"   - {word}")
    else:
        print(f"\n✅ All duplicate words have consistent gender and translation")
    
    return duplicates

if __name__ == "__main__":
    detailed_duplicate_analysis()