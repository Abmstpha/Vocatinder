from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import random
import os
from pathlib import Path

app = FastAPI(title="French Gender Swipe API", version="1.0.0")

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

@app.post("/api/generate-words")
async def generate_words():
    """Generate a random sample of 30 words from the words.json file"""
    try:
        if not WORDS_PATH.exists():
            raise HTTPException(status_code=404, detail="Words file not found")
        
        with open(WORDS_PATH, 'r', encoding='utf-8') as file:
            all_words = json.load(file)
        
        if not isinstance(all_words, list) or len(all_words) < 30:
            raise HTTPException(
                status_code=400, 
                detail="words.json must contain at least 30 words"
            )
        
        # Shuffle and select 30 random words
        selected_words = random.sample(all_words, 30)
        
        return {"words": selected_words}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON format in words file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load words: {str(e)}")

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
