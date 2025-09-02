"""
Mistral AI client for enhanced feedback and explanations
"""

import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv

load_dotenv()

class MistralFeedbackClient:
    def __init__(self):
        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        
        self.client = MistralClient(api_key=api_key)
        self.model = "mistral-tiny"
    
    def explain_gender_rule(self, word: str, correct_gender: str) -> str:
        """Get explanation for why a word has a specific gender"""
        prompt = f"""Explain in 1-2 sentences why the French word "{word}" is {correct_gender}. 
        Include any relevant grammar rules or patterns. Keep it concise and educational.
        Respond in English for learning purposes."""
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[ChatMessage(role="user", content=prompt)],
                max_tokens=100,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"The word '{word}' is {correct_gender}."
    
    def explain_sentence_error(self, sentence: str, target_word: str, correct_gender: str) -> str:
        """Explain why a sentence has incorrect gender agreement"""
        prompt = f"""This French sentence has a gender agreement error: "{sentence}"
        The word "{target_word}" should be {correct_gender}.
        Explain the error in 1-2 sentences. Keep it educational and concise.
        Respond in English."""
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[ChatMessage(role="user", content=prompt)],
                max_tokens=120,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Gender agreement error: '{target_word}' should use {correct_gender} articles."
