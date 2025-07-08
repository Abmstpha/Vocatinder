#!/usr/bin/env python3
"""
Script to analyze duplicate words in the French Gender Swipe JSON file.
Identifies all words that appear more than once and reports their frequencies.
"""

import json
from collections import Counter

def analyze_duplicates():
    """Analyze the words.json file to find duplicate words and their frequencies."""
    
    # Load the JSON data
    with open('public/words.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract just the words from the JSON data
    words = [entry['word'] for entry in data]
    
    # Count frequency of each word
    word_counts = Counter(words)
    
    # Find words that appear more than once
    duplicates = {word: count for word, count in word_counts.items() if count > 1}
    
    # Sort by frequency (descending) and then alphabetically
    sorted_duplicates = sorted(duplicates.items(), key=lambda x: (-x[1], x[0]))
    
    print("🔍 Analysis of duplicate words in public/words.json")
    print("=" * 50)
    print(f"Total entries in file: {len(data)}")
    print(f"Unique words: {len(word_counts)}")
    print(f"Words appearing more than once: {len(duplicates)}")
    print()
    
    if duplicates:
        print("📊 Duplicate words and their frequencies:")
        print("-" * 30)
        for word, count in sorted_duplicates:
            print(f"{word}: {count} times")
        
        # Summary statistics
        total_duplicate_occurrences = sum(duplicates.values())
        total_excess_duplicates = sum(count - 1 for count in duplicates.values())
        
        print()
        print("📈 Summary:")
        print(f"  - Total duplicate occurrences: {total_duplicate_occurrences}")
        print(f"  - Excess duplicate entries: {total_excess_duplicates}")
        print(f"  - If duplicates were removed, file would have: {len(data) - total_excess_duplicates} entries")
    else:
        print("✅ No duplicate words found!")
    
    return duplicates

if __name__ == "__main__":
    duplicates = analyze_duplicates()