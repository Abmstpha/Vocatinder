# Vocatinder - French Gender Swipe Game

A French language learning app with Tinder-style swipe interface, powered by FastAPI and Mistral AI.

## Project Structure

```
Vocatinder/
├── backend/          # FastAPI Python backend
│   ├── main.py       # FastAPI server
│   ├── requirements.txt
│   └── .env          # API keys
├── frontend/         # Static frontend files
│   ├── index.html    # Main UI
│   ├── words.json    # French words database
│   └── server.js     # Old Node.js server (deprecated)
└── README.md
```

## Setup & Run

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Access the app
- Frontend: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## API Endpoints

- `GET /` - Serve frontend
- `POST /api/generate-words` - Get 30 random French words
- `GET /health` - Health check
