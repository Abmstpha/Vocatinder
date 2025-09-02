from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import random
import os
import uuid
from pathlib import Path
from data_pipeline import FrenchNewsProcessor, FALLBACK_SENTENCES
from mistral_client import MistralFeedbackClient
from typing import List, Dict, Optional

class StartGameRequest(BaseModel):
    language_level: str = "beginner"

app = FastAPI(title="VocaTinder - French Gender Learning API", version="2.0.0")

# Initialize processors
news_processor = FrenchNewsProcessor()
mistral_client = MistralFeedbackClient()

# Store game sessions in memory (in production, use database)
game_sessions = {}

# Store game progress for multi-round games
class GameSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.challenges = []  # List of 10 challenges
        self.current_challenge_index = 0
        self.score = 0
        self.round_type = "sentence_check"  # Current round type
        self.current_target_noun = None
        
active_games = {}

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
async def start_game(request: StartGameRequest = StartGameRequest()) -> GameRound:
    """Start a new game and return the first round"""
    try:
        session_id = str(uuid.uuid4())
        
        # Generate game data using the news processor with language level
        news_processor = FrenchNewsProcessor()
        game_data = news_processor.generate_game_data(num_rounds=10, language_level=request.language_level)
        
        if not game_data or len(game_data) < 10:
            # Use fallback data if scraping fails
            challenges = []
            for i in range(10):
                fallback = random.choice(FALLBACK_SENTENCES)
                corrupted_sentence, is_correct = news_processor.corrupt_sentence(
                    fallback["original_sentence"], 
                    fallback["target_noun"]
                )
                challenges.append({
                    "original_sentence": fallback["original_sentence"],
                    "display_sentence": corrupted_sentence,
                    "target_noun": fallback["target_noun"],
                    "is_correct": is_correct
                })
        else:
            challenges = game_data[:10]
        
        # Create new game session
        session_id = f"game_{random.randint(10000, 99999)}"
        game_session = GameSession(session_id)
        game_session.challenges = challenges
        active_games[session_id] = game_session
        
        # Return first challenge
        first_challenge = challenges[0]
        round_id = f"{session_id}_challenge_0"
        
        return GameRound(
            round_id=round_id,
            round_type="sentence_check",
            display_text=first_challenge["display_sentence"],
            target_word=first_challenge["target_noun"]["word"],
            correct_answer=first_challenge["is_correct"],
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
        # Parse round_id to get session and challenge info
        if "_challenge_" in answer.round_id:
            session_id, challenge_part = answer.round_id.split("_challenge_")
            challenge_index = int(challenge_part)
            round_type = "sentence_check"
        elif "_word_" in answer.round_id:
            session_id, word_part = answer.round_id.split("_word_")
            challenge_index = int(word_part)
            round_type = "word_check"
        else:
            raise HTTPException(status_code=400, detail="Invalid round ID format")
        
        game_session = active_games.get(session_id)
        if not game_session:
            raise HTTPException(status_code=404, detail="Game session not found")
        
        current_challenge = game_session.challenges[challenge_index]
        
        if round_type == "sentence_check":
            user_correct = (answer.user_choice == "right" and current_challenge["is_correct"]) or \
                          (answer.user_choice == "left" and not current_challenge["is_correct"])
            
            if user_correct:
                game_session.score += 1
            
            # Always proceed to Round 2 (Word Check) regardless of Round 1 result
            target_noun = current_challenge["target_noun"]
            target_word = target_noun["word"]
            correct_gender = target_noun["gender"]
            
            # Get appropriate explanation
            if user_correct:
                explanation = f"Correct! Now identify the gender of '{target_word}'"
            else:
                explanation = mistral_client.explain_sentence_error(
                    current_challenge["original_sentence"],
                    current_challenge["target_noun"]["word"],
                    current_challenge["target_noun"]["gender"]
                )
                explanation += f" Now identify the gender of '{target_word}'"
            
            word_round_id = f"{session_id}_word_{challenge_index}"
            
            next_round = GameRound(
                round_id=word_round_id,
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
                is_correct=user_correct,
                explanation=explanation,
                correct_answer="Correct grammar" if user_correct else f"Correct: {current_challenge['original_sentence']}",
                next_round=next_round
            )
        
        elif round_type == "word_check":
            # Check gender answer
            target_noun = current_challenge["target_noun"]
            correct_gender = target_noun["gender"]
            user_gender_correct = (answer.user_choice == "right" and correct_gender == "masculine") or \
                                 (answer.user_choice == "left" and correct_gender == "feminine")
            
            if user_gender_correct:
                game_session.score += 1
                explanation = f"Excellent! '{target_noun['word']}' is indeed {correct_gender}."
            else:
                explanation = mistral_client.explain_gender_rule(
                    target_noun["word"], 
                    correct_gender
                )
            
            # Move to next challenge
            game_session.current_challenge_index += 1
            
            if game_session.current_challenge_index >= len(game_session.challenges):
                # Game complete
                return FeedbackResponse(
                    is_correct=user_gender_correct,
                    explanation=explanation,
                    correct_answer=f"'{target_noun['word']}' is {correct_gender}",
                    next_round=None
                )
            
            # Next challenge
            next_challenge = game_session.challenges[game_session.current_challenge_index]
            next_round_id = f"{session_id}_challenge_{game_session.current_challenge_index}"
            
            next_round = GameRound(
                round_id=next_round_id,
                round_type="sentence_check",
                display_text=next_challenge["display_sentence"],
                target_word=next_challenge["target_noun"]["word"],
                correct_answer=next_challenge["is_correct"],
                options={
                    "left": "Incorrect Grammar",
                    "right": "Correct Grammar"
                }
            )
            
            return FeedbackResponse(
                is_correct=user_gender_correct,
                explanation=explanation,
                correct_answer=f"'{target_noun['word']}' is {correct_gender}",
                next_round=next_round
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process answer: {str(e)}")

@app.get("/api/game-status/{session_id}")
async def get_game_status(session_id: str):
    """Get current game progress"""
    game_session = active_games.get(session_id)
    if not game_session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    return {
        "session_id": session_id,
        "current_challenge": game_session.current_challenge_index + 1,
        "total_challenges": len(game_session.challenges),
        "score": game_session.score,
        "progress_percentage": round((game_session.current_challenge_index / len(game_session.challenges)) * 100)
    }

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
