"""
Data pipeline for scraping French news headlines and processing them for the game
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import spacy
import random
from typing import List, Dict, Tuple
import json
from pathlib import Path

class FrenchNewsProcessor:
    def __init__(self):
        # Load French spaCy model (download with: python -m spacy download fr_core_news_sm)
        try:
            self.nlp = spacy.load("fr_core_news_sm")
        except OSError:
            print("⚠️  French spaCy model not found. Run: python -m spacy download fr_core_news_sm")
            self.nlp = None
    
    def scrape_french_news_rss(self) -> List[str]:
        """Scrape French news headlines from RSS feeds"""
        rss_feeds = [
            "https://www.lemonde.fr/rss/une.xml",
            "https://www.franceinfo.fr/rss/une.xml",
            "https://www.liberation.fr/rss/",
            "https://rss.cnn.com/rss/edition.rss"  # Backup international feed
        ]
        
        headlines = []
        
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:  # Get first 10 headlines per feed
                    headlines.append(entry.title)
            except Exception as e:
                print(f"Failed to fetch from {feed_url}: {e}")
                continue
        
        return headlines[:50]  # Return max 50 headlines
    
    def extract_nouns_with_gender(self, text: str) -> List[Dict]:
        """Extract French nouns with their grammatical gender using spaCy"""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        nouns_with_gender = []
        
        for token in doc:
            if token.pos_ == "NOUN" and len(token.text) > 2:
                # Determine gender based on article or morphological features
                gender = self._determine_gender(token, doc)
                if gender:
                    nouns_with_gender.append({
                        "word": token.text,
                        "lemma": token.lemma_,
                        "gender": gender,
                        "article": "le" if gender == "masculine" else "la",
                        "position": token.idx,
                        "sentence": text
                    })
        
        return nouns_with_gender
    
    def _determine_gender(self, token, doc) -> str:
        """Determine gender of a noun based on context and morphology"""
        # Look for articles before the noun
        for i in range(max(0, token.i - 3), token.i):
            prev_token = doc[i]
            if prev_token.text.lower() in ["le", "du", "au", "un"]:
                return "masculine"
            elif prev_token.text.lower() in ["la", "de la", "à la", "une"]:
                return "feminine"
        
        # Use morphological features if available
        if hasattr(token, 'morph') and token.morph:
            gender_feature = token.morph.get("Gender")
            if gender_feature:
                return "masculine" if "Masc" in gender_feature else "feminine"
        
        # Fallback: basic heuristics
        word_lower = token.text.lower()
        if word_lower.endswith(('tion', 'sion', 'ette', 'elle', 'ance', 'ence')):
            return "feminine"
        elif word_lower.endswith(('ment', 'age', 'isme', 'eau')):
            return "masculine"
        
        return None
    
    def corrupt_sentence(self, sentence: str, target_noun: Dict) -> Tuple[str, bool]:
        """Corrupt a sentence by randomly flipping gender of target noun"""
        should_corrupt = random.choice([True, False])
        
        if not should_corrupt:
            return sentence, True  # Correct sentence
        
        # Flip the article/adjective gender
        corrupted = sentence
        original_gender = target_noun["gender"]
        
        # Replace articles
        if original_gender == "masculine":
            corrupted = corrupted.replace(" le ", " la ")
            corrupted = corrupted.replace(" Le ", " La ")
            corrupted = corrupted.replace(" un ", " une ")
            corrupted = corrupted.replace(" Un ", " Une ")
        else:
            corrupted = corrupted.replace(" la ", " le ")
            corrupted = corrupted.replace(" La ", " Le ")
            corrupted = corrupted.replace(" une ", " un ")
            corrupted = corrupted.replace(" Une ", " Un ")
        
        return corrupted, False  # Incorrect sentence
    
    def generate_game_data(self, num_rounds: int = 20) -> List[Dict]:
        """Generate game data with corrupted and correct sentences"""
        headlines = self.scrape_french_news_rss()
        game_data = []
        
        for headline in headlines[:num_rounds]:
            nouns = self.extract_nouns_with_gender(headline)
            if nouns:
                target_noun = random.choice(nouns)
                corrupted_sentence, is_correct = self.corrupt_sentence(headline, target_noun)
                
                game_data.append({
                    "original_sentence": headline,
                    "display_sentence": corrupted_sentence,
                    "target_noun": target_noun,
                    "is_correct": is_correct,
                    "round_type": "sentence_check"
                })
        
        return game_data

# Fallback data if scraping fails
FALLBACK_SENTENCES = [
    {
        "original_sentence": "Le président français a donné une conférence de presse.",
        "target_noun": {"word": "président", "gender": "masculine", "article": "le"},
        "is_correct": True
    },
    {
        "original_sentence": "La ministre de l'éducation a annoncé de nouvelles réformes.",
        "target_noun": {"word": "ministre", "gender": "feminine", "article": "la"},
        "is_correct": True
    },
    {
        "original_sentence": "Le voiture rouge est garée devant la maison.",
        "target_noun": {"word": "voiture", "gender": "feminine", "article": "la"},
        "is_correct": False
    }
]
