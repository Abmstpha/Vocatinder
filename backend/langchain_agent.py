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
    
    for token in doc:
        if token.pos_ == "NOUN":
            # Look for gender indicators
            gender = "unknown"
            article_context = ""
            
            # Check preceding articles
            for i in range(max(0, token.i - 3), token.i):
                prev_token = doc[i]
                if prev_token.text.lower() in ["le", "du", "au", "un"]:
                    gender = "masculine"
                    article_context = prev_token.text
                    break
                elif prev_token.text.lower() in ["la", "de la", "à la", "une"]:
                    gender = "feminine"
                    article_context = prev_token.text
                    break
            
            if gender != "unknown":
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
    
    
    def intelligent_word_selection(self, sentence: str) -> Dict[str, Any]:
        """Use ReAct agent to intelligently select target word"""
        try:
            # Use the ReAct agent to reason about word selection
            result = self.agent.invoke({
                "messages": [
                    ("user", f"Analyze this French sentence and select the best target noun for gender learning: '{sentence}'. Use the tools to analyze structure, identify candidates, and select the optimal target.")
                ]
            })
            
            # Extract the final answer from agent response
            final_message = result["messages"][-1].content
            
            # Try to parse JSON from the final answer
            try:
                if "{" in final_message and "}" in final_message:
                    start = final_message.find("{")
                    end = final_message.rfind("}") + 1
                    json_str = final_message[start:end]
                    selected_word = json.loads(json_str)
                    return selected_word
            except:
                pass
            
            # Fallback to spaCy analysis if agent parsing fails
            return self._fallback_word_selection(sentence)
                
        except Exception as e:
            print(f"Agent error: {e}")
            return self._fallback_word_selection(sentence)
    
    def _fallback_word_selection(self, sentence: str) -> Dict[str, Any]:
        """Fallback word selection using spaCy"""
        doc = self.nlp(sentence)
        nouns_with_gender = []
        
        for token in doc:
            if token.pos_ == "NOUN":
                gender = self._determine_gender(token, doc)
                if gender != "unknown":
                    nouns_with_gender.append({
                        "word": token.text,
                        "gender": gender,
                        "article": self._get_article_context(token, doc),
                        "educational_value": self._calculate_educational_value(token, doc)
                    })
        
        if nouns_with_gender:
            return max(nouns_with_gender, key=lambda x: x["educational_value"])
        else:
            return {"word": "mot", "gender": "masculine", "article": "le"}
    
    def _determine_gender(self, token, doc):
        """Determine gender using context and morphology"""
        for i in range(max(0, token.i - 3), token.i):
            prev_token = doc[i]
            if prev_token.text.lower() in ["le", "du", "au", "un"]:
                return "masculine"
            elif prev_token.text.lower() in ["la", "de la", "à la", "une"]:
                return "feminine"
        return "unknown"
    
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
    
    def intelligent_sentence_restructuring(self, sentence: str, target_noun: Dict) -> tuple[str, bool]:
        """Use ReAct agent to intelligently restructure sentences"""
        try:
            # Use the ReAct agent to reason about sentence corruption
            result = self.agent.invoke({
                "messages": [
                    ("user", f"Decide how to create an educational grammar exercise from this French sentence: '{sentence}' with target noun '{target_noun['word']}' (gender: {target_noun['gender']}). Should it be corrupted or left correct? If corrupted, how?")
                ]
            })
            
            # For now, use existing corruption logic with 50/50 chance
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
            print(f"Agent restructuring error: {e}")
            # Fallback to original corruption logic
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
