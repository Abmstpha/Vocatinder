from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import random
import os
from pathlib import Path
from data_pipeline import FrenchNewsProcessor, FALLBACK_SENTENCES
from mistral_client import MistralFeedbackClient
from typing import List, Dict, Optional

app = FastAPI(title="VocaTinder - French Gender Learning API", version="2.0.0")

# Initialize processors
news_processor = FrenchNewsProcessor()
mistral_client = MistralFeedbackClient()

# Pydantic models
class GameRound(BaseModel):
    round_id: str
    round_type: str  # "sentence_check" or "word_check"
    display_text: str
    target_word: str
    correct_answer: bool
    options: Dict[str, str]

class UserAnswer(BaseModel):
    round_id: str
    user_choice: str  # "left" or "right"
    
class FeedbackResponse(BaseModel):
    is_correct: bool
    explanation: str
    correct_answer: str
    next_round: Optional[GameRound]

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the path to the words.json file in the backend folder
WORDS_PATH = Path(__file__).parent / "words.json"

# Mount static files from React build folder (will be created after npm run build)
# For development, React runs on port 3000, FastAPI on port 8000

@app.get("/")
async def serve_frontend():
    """Serve the main HTML file"""
    frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
    return FileResponse(frontend_path)

@app.post("/api/start-game")
async def start_game() -> GameRound:
    """Start a new game session with Round 1 (Sentence Check)"""
    try:
        # Try to get fresh news data, fallback to static data
        game_data = news_processor.generate_game_data(num_rounds=1)
        
        if not game_data:
            # Use fallback data if scraping fails
            fallback = random.choice(FALLBACK_SENTENCES)
            corrupted_sentence, is_correct = news_processor.corrupt_sentence(
                fallback["original_sentence"], 
                fallback["target_noun"]
            )
            
            return GameRound(
                round_id=f"round_{random.randint(1000, 9999)}",
                round_type="sentence_check",
                display_text=corrupted_sentence,
                target_word=fallback["target_noun"]["word"],
                correct_answer=is_correct,
                options={
                    "left": "Incorrect Grammar",
                    "right": "Correct Grammar"
                }
            )
        
        round_data = game_data[0]
        return GameRound(
            round_id=f"round_{random.randint(1000, 9999)}",
            round_type="sentence_check",
            display_text=round_data["display_sentence"],
            target_word=round_data["target_noun"]["word"],
            correct_answer=round_data["is_correct"],
            options={
                "left": "Incorrect Grammar",
                "right": "Correct Grammar"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate game: {str(e)}")

@app.post("/api/submit-answer")
async def submit_answer(answer: UserAnswer) -> FeedbackResponse:
    """Submit user answer and get feedback + next round"""
    try:
        # For demo purposes, we'll simulate the game logic
        # In a real app, you'd store game state in a database
        
        # Simulate Round 1 -> Round 2 progression
        is_round1_correct = random.choice([True, False])  # Simulate answer checking
        
        if is_round1_correct:
            # Generate Round 2 (Word Check)
            target_word = "maison"  # Example word
            correct_gender = "feminine"
            
            explanation = mistral_client.explain_gender_rule(target_word, correct_gender)
            
            next_round = GameRound(
                round_id=f"round_{random.randint(1000, 9999)}",
                round_type="word_check",
                display_text=target_word,
                target_word=target_word,
                correct_answer=True,  # Will be determined by user's swipe
                options={
                    "left": "Feminine (LA)",
                    "right": "Masculine (LE)"
                }
            )
            
            return FeedbackResponse(
                is_correct=True,
                explanation="Correct! Now identify the gender of this word:",
                correct_answer="Correct grammar",
                next_round=next_round
            )
        else:
            explanation = mistral_client.explain_sentence_error(
                "Example sentence", "example word", "feminine"
            )
            
            return FeedbackResponse(
                is_correct=False,
                explanation=explanation,
                correct_answer="The sentence had incorrect gender agreement",
                next_round=None
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process answer: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "🇫🇷 French Gender Swipe API is running!"}

if __name__ == "__main__":
    import uvicorn
    print("🇫🇷 French Gender Swipe Game API")
    print("🚀 Starting FastAPI server...")
    print("📚 Serving words from: frontend/words.json")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
