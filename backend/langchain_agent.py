import os
from typing import Dict, List, Any
from langchain_core.tools import tool
from langchain_mistralai import ChatMistralAI
from langgraph.prebuilt import create_react_agent
import spacy
import random
import json

@tool
def analyze_sentence_structure(sentence: str) -> str:
    """Analyze French sentence structure to identify key grammatical elements"""
    nlp = spacy.load("fr_core_news_sm")
    doc = nlp(sentence)
    
    analysis = {
        "nouns": [],
        "articles": [],
        "structure": []
    }
    
    for token in doc:
        if token.pos_ == "NOUN":
            analysis["nouns"].append({
                "word": token.text,
                "position": token.i,
                "dependency": token.dep_
            })
        elif token.pos_ == "DET":
            analysis["articles"].append({
                "word": token.text,
                "position": token.i
            })
        
        analysis["structure"].append(f"{token.text}({token.pos_})")
    
    return json.dumps(analysis)

@tool
def identify_target_nouns(sentence: str) -> str:
    """Identify nouns with clear gender markers that would make good learning targets"""
    nlp = spacy.load("fr_core_news_sm")
    doc = nlp(sentence)
    candidates = []
    
    def determine_gender_enhanced(token, doc):
        """Enhanced gender determination with fallbacks"""
        # Check surrounding articles (3 words before and after)
        for i in range(max(0, token.i - 3), min(len(doc), token.i + 3)):
            context_token = doc[i]
            text_lower = context_token.text.lower()
            
            # Masculine indicators
            if text_lower in ["le", "du", "au", "un", "ce", "cet", "mon", "ton", "son"]:
                return "masculine"
            # Feminine indicators  
            elif text_lower in ["la", "de la", "à la", "une", "cette", "ma", "ta", "sa"]:
                return "feminine"
        
        # Fallback: Use common French word endings
        word_lower = token.text.lower()
        
        # Common feminine endings
        if word_lower.endswith(('tion', 'sion', 'ure', 'ence', 'ance', 'ette', 'elle', 'esse')):
            return "feminine"
        # Common masculine endings
        elif word_lower.endswith(('ment', 'age', 'isme', 'eau', 'ou')):
            return "masculine"
        
        # Default to masculine (more common in French)
        return "masculine"
    
    for token in doc:
        if token.pos_ == "NOUN" and len(token.text) > 2:
            # Use enhanced gender determination
            gender = determine_gender_enhanced(token, doc)
            article_context = ""
            
            # Find the closest article for context
            for i in range(max(0, token.i - 3), token.i):
                prev_token = doc[i]
                if prev_token.text.lower() in ["le", "du", "au", "un", "la", "de la", "à la", "une"]:
                    article_context = prev_token.text
                    break
            
            candidates.append({
                "word": token.text,
                "gender": gender,
                "article": article_context,
                "position": token.i,
                    "dependency": token.dep_
                })
    
    return json.dumps(candidates)

@tool
def select_optimal_target(candidates_json: str) -> str:
    """Select the best target noun from candidates for educational purposes"""
    try:
        candidates = json.loads(candidates_json)
        if not candidates:
            return json.dumps({"error": "No suitable candidates found"})
        
        # Score candidates based on educational value
        for candidate in candidates:
            score = 0
            
            # Prefer nouns with clear articles
            if candidate.get("article", "").lower() in ["le", "la", "un", "une"]:
                score += 3
            
            # Prefer subject/object nouns (more central to meaning)
            if candidate.get("dependency") in ["nsubj", "dobj"]:
                score += 2
            
            # Prefer earlier position in sentence (more prominent)
            if candidate.get("position", 10) < 5:
                score += 1
            
            candidate["score"] = score
        
        # Select highest scoring candidate
        best_candidate = max(candidates, key=lambda x: x.get("score", 0))
        return json.dumps(best_candidate)
        
    except Exception as e:
        return json.dumps({"error": f"Error processing candidates: {str(e)}"})

class FrenchGrammarAgent:
    def __init__(self, api_key: str):
        self.llm = ChatMistralAI(
            model="mistral-small-latest",
            mistral_api_key=api_key,
            temperature=0.3
        )
        self.nlp = spacy.load("fr_core_news_sm")
        
        # Create ReAct agent with tools
        self.agent = create_react_agent(
            model=self.llm,
            tools=[
                analyze_sentence_structure,
                identify_target_nouns,
                select_optimal_target
            ]
        )
    
    
    def intelligent_word_selection(self, sentence: str, language_level: str = "beginner") -> Dict:
        """Use ReAct agent to select the best target word for educational purposes"""
        try:
            # Extract nouns first as fallback
            nouns = self._extract_nouns_with_gender(sentence)
            if not nouns:
                raise Exception("No suitable nouns found")
            
            # Use simple scoring for now (skip ReAct agent to avoid timeouts)
            best_noun = max(nouns, key=lambda n: len(n["word"]))  # Simple fallback scoring
            return best_noun
            
        except Exception as e:
            print(f"Word selection error: {e}")
            return self._fallback_word_selection(sentence)
    
    def _extract_nouns_with_gender(self, sentence: str) -> List[Dict]:
        """Extract nouns with gender information from sentence"""
        doc = self.nlp(sentence)
        nouns_with_gender = []
        
        for token in doc:
            if token.pos_ == "NOUN" and len(token.text) > 2:
                # Determine gender based on surrounding articles
                gender = self._determine_gender(token, doc)
                print(f"DEBUG: Word '{token.text}' detected gender: {gender}")
                
                # Always add the noun since _determine_gender now never returns "unknown"
                nouns_with_gender.append({
                    "word": token.text,
                    "gender": gender,
                    "lemma": token.lemma_
                })
        
        print(f"DEBUG: Found {len(nouns_with_gender)} nouns with gender")
        return nouns_with_gender
    
    def _fallback_word_selection(self, sentence: str) -> Dict[str, Any]:
        """Fallback word selection using spaCy"""
        nouns = self._extract_nouns_with_gender(sentence)
        if not nouns:
            raise Exception("No suitable nouns found in sentence")
        return random.choice(nouns)
    
    def _determine_gender(self, token, doc):
        """Determine gender using context and morphology"""
        # Check surrounding articles (3 words before and after)
        for i in range(max(0, token.i - 3), min(len(doc), token.i + 3)):
            context_token = doc[i]
            text_lower = context_token.text.lower()
            
            # Masculine indicators
            if text_lower in ["le", "du", "au", "un", "ce", "cet", "mon", "ton", "son"]:
                return "masculine"
            # Feminine indicators  
            elif text_lower in ["la", "de la", "à la", "une", "cette", "ma", "ta", "sa"]:
                return "feminine"
        
        # Fallback: Use common French word endings
        word_lower = token.text.lower()
        
        # Common feminine endings
        if word_lower.endswith(('tion', 'sion', 'ure', 'ence', 'ance', 'ette', 'elle', 'esse')):
            return "feminine"
        # Common masculine endings
        elif word_lower.endswith(('ment', 'age', 'isme', 'eau', 'ou')):
            return "masculine"
        
        # Default to masculine (more common in French)
        return "masculine"
    
    def _get_article_context(self, token, doc):
        """Get article context for a noun"""
        context = []
        for i in range(max(0, token.i - 2), min(len(doc), token.i + 3)):
            if doc[i].pos_ in ["DET", "ADP"]:
                context.append(doc[i].text)
        return " ".join(context)
    
    def _calculate_educational_value(self, token, doc):
        """Calculate educational value of a noun for gender learning"""
        score = 0
        if token.dep_ in ["nsubj", "dobj"]:
            score += 2
        if len(token.text) <= 6:
            score += 1
        return score
    
    def intelligent_sentence_restructuring(self, sentence: str, target_noun: Dict, language_level: str = "beginner") -> tuple[str, bool]:
        """Use ReAct agent to intelligently restructure sentences"""
        try:
            # Skip ReAct agent to avoid timeouts, use direct logic
            should_corrupt = random.choice([True, False])
            
            if not should_corrupt:
                return sentence, True
            
            # Apply corruption based on target noun gender
            corrupted = sentence
            original_gender = target_noun["gender"]
            
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
            
            return corrupted, False
            
        except Exception as e:
            print(f"Sentence restructuring failed: {e}")
            # Fallback to simple corruption
            return self._fallback_sentence_corruption(sentence, target_noun)

    def _fallback_sentence_corruption(self, sentence: str, target_noun: Dict) -> tuple[str, bool]:
        should_corrupt = random.choice([True, False])
        if not should_corrupt:
            return sentence, True
        
        corrupted = sentence
        original_gender = target_noun["gender"]
        
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
        
        return corrupted, False
