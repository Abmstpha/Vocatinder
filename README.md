# Vocatinder - French Gender Swipe Game

A French language learning app with Tinder-style swipe interface, powered by FastAPI and Mistral AI.

## Project Structure

```
Vocatinder/
├── backend/          # FastAPI Python backend
│   ├── main.py       # FastAPI server
│   ├── requirements.txt
│   ├── words.json    # French words database
│   └── .env          # API keys
├── frontend/         # React TypeScript frontend
│   ├── public/       # React public assets
│   ├── src/          # React source code
│   │   ├── components/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## Setup & Run

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend (React TypeScript)
```bash
cd frontend
npm install
npm start
```

### Access the app
- React frontend: http://localhost:3000
- FastAPI backend: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## API Endpoints

- `GET /` - Serve frontend
- `POST /api/generate-words` - Get 30 random French words
- `GET /health` - Health check
