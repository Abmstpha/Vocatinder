#!/usr/bin/env python3
"""
Generate a JSON report of duplicate words for programmatic use.
"""

import json
from collections import Counter

def generate_json_report():
    """Generate a JSON report of duplicate words."""
    
    # Load the JSON data
    with open('public/words.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract words and count frequencies
    words = [entry['word'] for entry in data]
    word_counts = Counter(words)
    
    # Find duplicates
    duplicates = {word: count for word, count in word_counts.items() if count > 1}
    
    # Prepare the report
    report = {
        "summary": {
            "total_entries": len(data),
            "unique_words": len(word_counts),
            "duplicate_words_count": len(duplicates),
            "total_duplicate_occurrences": sum(duplicates.values()),
            "excess_duplicate_entries": sum(count - 1 for count in duplicates.values())
        },
        "duplicates": {}
    }
    
    # Add each duplicate word with its frequency
    for word, count in sorted(duplicates.items(), key=lambda x: (-x[1], x[0])):
        report["duplicates"][word] = count
    
    # Save to JSON file
    with open('duplicate_words_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("JSON report generated: duplicate_words_report.json")
    print(f"Found {len(duplicates)} duplicate words with {sum(duplicates.values())} total occurrences")
    
    return report

if __name__ == "__main__":
    generate_json_report()