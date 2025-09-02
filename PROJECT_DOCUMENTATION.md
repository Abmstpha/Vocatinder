# VocaTinder - French Gender Learning Game

## Project Overview

VocaTinder is an innovative French language learning application that gamifies the challenging task of learning French noun genders. The app uses a Tinder-like swipe interface combined with real French news headlines to create an engaging and educational experience.

## Architecture

### Frontend (React TypeScript)
- **Framework**: React 18 with TypeScript
- **UI Components**: Custom swipe cards, game statistics, feedback modals, and language level selector
- **Styling**: CSS with modern responsive design
- **Interaction**: Swipe gestures and keyboard controls (arrow keys)

### Backend (FastAPI Python)
- **Framework**: FastAPI for REST API
- **AI Integration**: Mistral AI for educational feedback and explanations
- **NLP Processing**: spaCy French model (`fr_core_news_sm`) for linguistic analysis
- **Intelligent Agent**: LangChain ReAct agent for smart word selection and sentence restructuring
- **Data Source**: Real-time French news scraping from RSS feeds

## Game Mechanics

### Two-Round Challenge System
Each game consists of 10 challenges, with each challenge having two rounds:

1. **Round 1 - Sentence Check**: 
   - Display a French sentence (either correct or grammatically corrupted)
   - Player swipes right for "Correct Grammar" or left for "Incorrect Grammar"
   - Immediate feedback with explanation

2. **Round 2 - Word Check**:
   - Display the target noun from the sentence
   - Player swipes right for "Masculine (LE)" or left for "Feminine (LA)"
   - Detailed gender rule explanation from Mistral AI

### Key Features
- **Continuous Play**: Players can continue through all 10 challenges regardless of wrong answers
- **Dynamic Content**: Fresh French news headlines scraped for each game session
- **Temporal Memory**: Headlines are tracked per session to avoid repetition within the same game
- **Language Level Adaptation**: Beginner, Intermediate, and Advanced levels affect AI reasoning
- **Intelligent Word Selection**: ReAct agent selects educationally valuable target words
- **Real-time Feedback**: Mistral AI provides contextual explanations for mistakes

## Technical Stack

### Backend Dependencies
```
fastapi==0.104.1
uvicorn==0.24.0
spacy==3.7.2
mistralai==0.0.12
langchain==0.1.0
langchain-mistralai==0.1.0
langgraph==0.0.26
feedparser==6.0.10
beautifulsoup4==4.12.2
requests==2.31.0
python-multipart==0.0.6
```

### Frontend Dependencies
```
react: ^18.2.0
typescript: ^4.9.5
@types/react: ^18.2.43
@types/react-dom: ^18.2.17
```

## AI Integration

### Mistral AI
- **Purpose**: Generate educational feedback and explanations
- **Usage**: Explain grammar errors and gender rules
- **API Key**: Required in backend `.env` file as `MISTRAL_API_KEY`

### LangChain ReAct Agent
- **Purpose**: Intelligent word selection and sentence analysis
- **Tools**: 
  - `analyze_sentence_structure`: Analyzes French sentence grammar
  - `identify_target_nouns`: Finds suitable nouns for gender exercises
  - `select_optimal_target`: Scores and selects best educational target
- **Language Level Integration**: Agent reasoning adapts based on user's proficiency level

### spaCy NLP
- **Model**: `fr_core_news_sm` (French language model)
- **Usage**: Noun extraction, gender determination, linguistic analysis
- **Fallback**: Used when ReAct agent fails

## Data Pipeline

### News Scraping
- **Sources**: Multiple French RSS feeds (Le Monde, France24, RFI, etc.)
- **Processing**: Real-time headline extraction and cleaning
- **Filtering**: Sentences with identifiable French nouns
- **Memory**: Temporal tracking to avoid repetition within game sessions

### Sentence Corruption
- **Method**: Intelligent article/adjective swapping based on target noun gender
- **Examples**:
  - "Le chat" → "La chat" (masculine to feminine corruption)
  - "Une voiture" → "Un voiture" (feminine to masculine corruption)

## File Structure

```
Vocatinder/
├── backend/
│   ├── main.py                 # FastAPI server and game logic
│   ├── data_pipeline.py        # News scraping and NLP processing
│   ├── langchain_agent.py      # ReAct agent implementation
│   ├── mistral_client.py       # Mistral AI integration
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables (MISTRAL_API_KEY)
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Main React component
│   │   ├── types/index.ts     # TypeScript interfaces
│   │   └── components/
│   │       ├── SwipeCard.tsx      # Swipe interaction component
│   │       ├── GameStats.tsx      # Score and progress display
│   │       ├── FeedbackModal.tsx  # Feedback overlay
│   │       └── LevelSelector.tsx  # Language level selection
│   ├── package.json           # Node.js dependencies
│   └── public/                # Static assets
└── README.md
```

## API Endpoints

### POST /api/start-game
- **Purpose**: Initialize new game session
- **Input**: `{ language_level: "beginner" | "intermediate" | "advanced" }`
- **Output**: First game round with sentence and options
- **Process**: Scrapes news, generates 10 challenges, returns first round

### POST /api/submit-answer
- **Purpose**: Process user answer and return feedback
- **Input**: `{ round_id: string, user_choice: "left" | "right" }`
- **Output**: Feedback with explanation and next round (if applicable)
- **Process**: Validates answer, updates score, provides Mistral AI explanation

## Game State Management

### Frontend State
```typescript
interface GameState {
  currentRound: GameRound | null;
  score: number;
  totalRounds: number;
  gameComplete: boolean;
  roundsCompleted: number;
  showFeedback: boolean;
  lastFeedback?: FeedbackResponse;
  languageLevel: LanguageLevel;
}
```

### Backend Session
```python
class GameSession:
    session_id: str
    challenges: List[Dict]
    current_challenge_index: int
    score: int
    language_level: str
```

## Educational Design

### Learning Objectives
1. **Grammar Recognition**: Identify correct vs incorrect French sentence structure
2. **Gender Mastery**: Learn masculine/feminine noun classifications
3. **Contextual Learning**: Use real-world French content for authentic language exposure
4. **Progressive Difficulty**: Adapt content complexity based on user language level

### Pedagogical Features
- **Immediate Feedback**: Instant explanations for both correct and incorrect answers
- **Spaced Repetition**: Varied content prevents memorization, encourages understanding
- **Contextual Learning**: Real news headlines provide authentic French usage
- **Adaptive Difficulty**: Language level selection tailors content complexity

## Development Setup

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
echo "MISTRAL_API_KEY=your_api_key_here" > .env
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm start  # Development server on port 3000
```

## Environment Variables
- `MISTRAL_API_KEY`: Required for Mistral AI integration (backend/.env)

## Key Innovations

1. **Real-time Content**: Dynamic news scraping ensures fresh, relevant content
2. **AI-Powered Selection**: ReAct agent intelligently chooses educational target words
3. **Adaptive Learning**: Language level integration personalizes difficulty
4. **Gamified UX**: Tinder-like swipes make grammar learning engaging
5. **Comprehensive Feedback**: Mistral AI provides detailed explanations for learning

## Future Enhancements

- **User Profiles**: Persistent progress tracking and spaced repetition
- **Performance Analytics**: Detailed learning analytics and weak area identification
- **Content Expansion**: Additional French grammar concepts beyond gender
- **Mobile App**: Native iOS/Android versions
- **Multiplayer**: Competitive learning with friends

## Technical Considerations

### Performance
- **Caching**: News headlines cached per session to reduce API calls
- **Fallback Logic**: Multiple layers of fallback ensure app never breaks
- **Async Processing**: Non-blocking news scraping and AI processing

### Scalability
- **Session Management**: In-memory storage (production would use database)
- **API Rate Limits**: Mistral API usage optimized to minimize costs
- **Error Handling**: Comprehensive error handling with graceful degradation

This project represents a sophisticated blend of modern web development, natural language processing, and AI-powered education, creating an engaging and effective French learning experience.
