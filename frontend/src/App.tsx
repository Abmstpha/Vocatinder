import React, { useState, useEffect } from 'react';
import SwipeCard from './components/SwipeCard';
import GameStats from './components/GameStats';
import FeedbackModal from './components/FeedbackModal';
import LevelSelector from './components/LevelSelector';
import { GameRound, GameState, FeedbackResponse, UserAnswer, LanguageLevel } from './types';
import './App.css';

const App: React.FC = () => {
  const [gameState, setGameState] = useState<GameState>({
    currentRound: null,
    score: 0,
    totalRounds: 10,
    gameComplete: false,
    roundsCompleted: 0,
    showFeedback: false,
    languageLevel: 'beginner'
  });
  const [levelSelected, setLevelSelected] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  // Handle level change
  const handleLevelChange = (level: LanguageLevel) => {
    setGameState(prev => ({
      ...prev,
      languageLevel: level
    }));
    setLevelSelected(true);
  };

  // Start new game
  const startGame = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/start-game', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language_level: gameState.languageLevel })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const gameRound: GameRound = await response.json();
      setGameState(prev => ({
        ...prev,
        currentRound: gameRound,
        score: 0,
        totalRounds: 10,
        gameComplete: false,
        roundsCompleted: 0,
        showFeedback: false
      }));
      setError('');
    } catch (err) {
      setError('Failed to start game. Make sure the backend is running!');
      console.error('Error starting game:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle swipe action
  const handleSwipe = async (direction: 'left' | 'right') => {
    if (!gameState.currentRound) return;

    try {
      const answer: UserAnswer = {
        round_id: gameState.currentRound.round_id,
        user_choice: direction
      };

      const response = await fetch('/api/submit-answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(answer)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const feedback: FeedbackResponse = await response.json();
      
      setGameState(prev => ({
        ...prev,
        showFeedback: true,
        lastFeedback: feedback,
        currentRound: feedback.next_round || null,
        gameComplete: !feedback.next_round,
        roundsCompleted: feedback.next_round ? prev.roundsCompleted : prev.roundsCompleted + 1
      }));

    } catch (err) {
      setError('Failed to submit answer');
      console.error('Error submitting answer:', err);
    }
  };

  // Continue to next round or restart
  const handleContinue = () => {
    if (gameState.lastFeedback?.next_round) {
      setGameState(prev => ({
        ...prev,
        showFeedback: false,
        currentRound: prev.lastFeedback?.next_round || null
      }));
    } else {
      startGame(); // Start new game
    }
  };

  useEffect(() => {
    setLoading(false); // Don't auto-start game, wait for level selection
  }, []);

  if (loading) {
    return (
      <div className="app">
        <div className="loading">
          <h2>🇫🇷 Loading VocaTinder...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <h1>🇫🇷 VocaTinder</h1>
      <p>Swipe to learn French vocab and gender nouns</p>
      
      {!levelSelected && !loading && (
        <LevelSelector 
          selectedLevel={gameState.languageLevel}
          onLevelChange={handleLevelChange}
          disabled={loading}
        />
      )}
      
      {levelSelected && !gameState.currentRound && (
        <GameStats gameState={gameState} />
      )}
      
      {error && <div className="error">{error}</div>}
      
      {loading ? (
        <div className="loading">Loading...</div>
      ) : gameState.currentRound ? (
        <SwipeCard 
          gameRound={gameState.currentRound} 
          onSwipe={handleSwipe}
        />
      ) : levelSelected ? (
        <button 
          onClick={startGame} 
          className="start-button"
          onKeyDown={(e) => {
            if (e.key === 'ArrowUp' || e.key === 'ArrowDown' || e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
              e.preventDefault();
              e.stopPropagation();
            }
          }}
        >
          {gameState.gameComplete ? 'Play Again' : 'Start Game'}
        </button>
      ) : null}
      
      {gameState.showFeedback && gameState.lastFeedback && (
        <FeedbackModal 
          feedback={gameState.lastFeedback}
          onContinue={handleContinue}
        />
      )}
    </div>
  );
};

export default App;
