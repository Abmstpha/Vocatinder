"""
Data pipeline for scraping French news headlines and processing them for the game
"""

import feedparser
import spacy
import random
import requests
import feedparser
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple
from langchain_agent import FrenchGrammarAgent
import os
import json
from pathlib import Path

class FrenchNewsProcessor:
    def __init__(self):
        # Load French spaCy model (download with: python -m spacy download fr_core_news_sm)
        try:
            self.nlp = spacy.load("fr_core_news_sm")
        except OSError:
            print("⚠️  French spaCy model not found. Run: python -m spacy download fr_core_news_sm")
            raise
        
        # Initialize LangChain ReAct agent
        api_key = os.getenv("MISTRAL_API_KEY")
        if api_key:
            try:
                self.grammar_agent = FrenchGrammarAgent(api_key)
                self.use_agent = True
                print("✅ LangChain ReAct agent initialized with Mistral")
            except Exception as e:
                print(f"⚠️  Failed to initialize LangChain agent: {e}")
                self.use_agent = False
        else:
            print("⚠️  MISTRAL_API_KEY not found, using fallback logic")
            self.use_agent = False
            
        # Cache for headlines with timestamp
        self._headline_cache = {"headlines": [], "timestamp": 0}
        self._cache_duration = 300  # 5 minutes cache
    
    def scrape_french_news_rss(self, force_refresh: bool = False) -> List[str]:
        """Scrape French news headlines from RSS feeds with smart caching"""
        import time
        
        current_time = time.time()
        
        # Check if we have fresh cached headlines
        if not force_refresh and self._headline_cache["headlines"] and \
           (current_time - self._headline_cache["timestamp"]) < self._cache_duration:
            print(f"📋 Using cached headlines ({len(self._headline_cache['headlines'])} available)")
            return self._headline_cache["headlines"].copy()
        
        print("🔄 Scraping fresh headlines...")
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
        
        # Update cache with fresh headlines
        self._headline_cache = {
            "headlines": headlines[:50],  # Store max 50 headlines
            "timestamp": current_time
        }
        
        print(f"✅ Cached {len(headlines[:50])} fresh headlines")
        return headlines[:50]
    
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
    
    def generate_game_data(self, num_rounds: int = 20, language_level: str = "beginner") -> List[Dict]:
        """Generate game data with corrupted and correct sentences - fresh scraping each time"""
        print(f"🔄 Starting fresh headline scraping for {language_level} level...")
        
        # Always scrape fresh headlines
        headlines = self.scrape_french_news_rss()
        print(f"📰 Scraped {len(headlines)} fresh headlines")
        
        # Randomize headline order for variety
        random.shuffle(headlines)
        
        # Filter headlines by complexity based on language level
        filtered_headlines = self._filter_headlines_by_level(headlines, language_level)
        print(f"🎯 Filtered to {len(filtered_headlines)} headlines for {language_level} level")
        
        game_data = []
        used_headlines = set()
        
        # Ensure we get enough unique headlines
        while len(game_data) < num_rounds and len(used_headlines) < len(filtered_headlines):
            for headline in filtered_headlines:
                if len(game_data) >= num_rounds:
                    break
                    
                # Skip if already used
                if headline in used_headlines:
                    continue
                    
                used_headlines.add(headline)
                nouns = self.extract_nouns_with_gender(headline)
                
                if nouns:
                    # Use LangChain ReAct agent for intelligent word selection
                    if self.use_agent:
                        try:
                            target_noun = self.grammar_agent.intelligent_word_selection(headline, language_level)
                            corrupted_sentence, is_correct = self.grammar_agent.intelligent_sentence_restructuring(headline, target_noun, language_level)
                        except Exception as e:
                            print(f"Agent failed, using fallback: {e}")
                            target_noun = random.choice(nouns)
                            corrupted_sentence, is_correct = self.corrupt_sentence(headline, target_noun)
                    else:
                        target_noun = random.choice(nouns)
                        corrupted_sentence, is_correct = self.corrupt_sentence(headline, target_noun)
                    
                    game_data.append({
                        "original_sentence": headline,
                        "display_sentence": corrupted_sentence,
                        "target_noun": target_noun,
                        "is_correct": is_correct,
                        "round_type": "sentence_check"
                    })
        
        # If still not enough, scrape more feeds or use variations
        if len(game_data) < num_rounds:
            # Re-scrape to get fresh headlines
            fresh_headlines = self.scrape_french_news_rss()
            for headline in fresh_headlines:
                if len(game_data) >= num_rounds:
                    break
                if headline not in used_headlines:
                    nouns = self.extract_nouns_with_gender(headline)
                    if nouns:
                        # Use LangChain ReAct agent for intelligent word selection
                        if self.use_agent:
                            try:
                                target_noun = self.grammar_agent.intelligent_word_selection(headline)
                                corrupted_sentence, is_correct = self.grammar_agent.intelligent_sentence_restructuring(headline, target_noun)
                            except Exception as e:
                                print(f"Agent failed, using fallback: {e}")
                                target_noun = random.choice(nouns)
                                corrupted_sentence, is_correct = self.corrupt_sentence(headline, target_noun)
                        else:
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
    
    def _filter_headlines_by_level(self, headlines: List[str], language_level: str) -> List[str]:
        """Filter headlines based on complexity for different language levels"""
        filtered = []
        
        for headline in headlines:
            # Analyze headline complexity
            doc = self.nlp(headline)
            word_count = len([token for token in doc if token.is_alpha])
            complex_words = len([token for token in doc if len(token.text) > 8])
            subordinate_clauses = len([token for token in doc if token.dep_ in ["mark", "advcl"]])
            
            # Level-based filtering
            if language_level == "beginner":
                # Simple headlines: 3-10 words, minimal complex vocabulary
                if 3 <= word_count <= 10 and complex_words <= 2 and subordinate_clauses == 0:
                    filtered.append(headline)
            elif language_level == "intermediate":
                # Medium headlines: 5-15 words, some complex vocabulary
                if 5 <= word_count <= 15 and complex_words <= 4:
                    filtered.append(headline)
            else:  # advanced
                # All headlines acceptable, prefer longer/complex ones
                if word_count >= 6:
                    filtered.append(headline)
        
        # If filtering is too restrictive, return random subset of all headlines
        if len(filtered) < 20:
            print(f"⚠️  Filtering too restrictive for {language_level}, using broader selection")
            random.shuffle(headlines)
            return headlines[:50]  # Return larger pool for variety
            
        return filtered

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
