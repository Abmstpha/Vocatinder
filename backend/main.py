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

# Store game sessions in memory (in production, use database)
game_sessions = {}

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
        # Get fresh news data or use fallback
        game_data = news_processor.generate_game_data(num_rounds=1)
        
        if not game_data:
            # Use fallback data if scraping fails
            fallback = random.choice(FALLBACK_SENTENCES)
            corrupted_sentence, is_correct = news_processor.corrupt_sentence(
                fallback["original_sentence"], 
                fallback["target_noun"]
            )
            
            round_id = f"round_{random.randint(1000, 9999)}"
            
            # Store session data
            game_sessions[round_id] = {
                "original_sentence": fallback["original_sentence"],
                "target_noun": fallback["target_noun"],
                "is_correct": is_correct,
                "round_type": "sentence_check"
            }
            
            return GameRound(
                round_id=round_id,
                round_type="sentence_check",
                display_text=corrupted_sentence,
                target_word=fallback["target_noun"]["word"],
                correct_answer=is_correct,
                options={
                    "left": "Incorrect Grammar",
                    "right": "Correct Grammar"
                }
            )
        
        # Use scraped data
        round_data = game_data[0]
        round_id = f"round_{random.randint(1000, 9999)}"
        
        # Store session data
        game_sessions[round_id] = {
            "original_sentence": round_data["original_sentence"],
            "target_noun": round_data["target_noun"],
            "is_correct": round_data["is_correct"],
            "round_type": "sentence_check"
        }
        
        return GameRound(
            round_id=round_id,
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
        # Get stored game session
        session = game_sessions.get(answer.round_id)
        if not session:
            raise HTTPException(status_code=404, detail="Game session not found")
        
        # Check user's answer
        user_correct = (answer.user_choice == "right" and session["is_correct"]) or \
                      (answer.user_choice == "left" and not session["is_correct"])
        
        if session["round_type"] == "sentence_check":
            if user_correct:
                # User got Round 1 correct - proceed to Round 2 (Word Check)
                target_noun = session["target_noun"]
                target_word = target_noun["word"]
                correct_gender = target_noun["gender"]
                
                # Get Mistral explanation for the word's gender
                explanation = mistral_client.explain_gender_rule(target_word, correct_gender)
                
                # Create Round 2
                round2_id = f"word_{random.randint(1000, 9999)}"
                game_sessions[round2_id] = {
                    "target_word": target_word,
                    "correct_gender": correct_gender,
                    "round_type": "word_check"
                }
                
                next_round = GameRound(
                    round_id=round2_id,
                    round_type="word_check",
                    display_text=target_word,
                    target_word=target_word,
                    correct_answer=(correct_gender == "masculine"),
                    options={
                        "left": "Feminine (LA)",
                        "right": "Masculine (LE)"
                    }
                )
                
                return FeedbackResponse(
                    is_correct=True,
                    explanation=f"Correct! Now identify the gender of '{target_word}': {explanation}",
                    correct_answer="Correct grammar",
                    next_round=next_round
                )
            else:
                # User got Round 1 wrong - explain the grammar error
                explanation = mistral_client.explain_sentence_error(
                    session["original_sentence"],
                    session["target_noun"]["word"],
                    session["target_noun"]["gender"]
                )
                
                return FeedbackResponse(
                    is_correct=False,
                    explanation=explanation,
                    correct_answer=f"The correct sentence: {session['original_sentence']}",
                    next_round=None
                )
        
        elif session["round_type"] == "word_check":
            # Round 2: Check if user identified gender correctly
            correct_gender = session["correct_gender"]
            user_gender_correct = (answer.user_choice == "right" and correct_gender == "masculine") or \
                                 (answer.user_choice == "left" and correct_gender == "feminine")
            
            if user_gender_correct:
                explanation = f"Excellent! '{session['target_word']}' is indeed {correct_gender}."
            else:
                explanation = mistral_client.explain_gender_rule(
                    session["target_word"], 
                    correct_gender
                )
            
            return FeedbackResponse(
                is_correct=user_gender_correct,
                explanation=explanation,
                correct_answer=f"'{session['target_word']}' is {correct_gender}",
                next_round=None  # Game complete
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
