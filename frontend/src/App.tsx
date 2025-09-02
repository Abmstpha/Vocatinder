import React, { useState, useEffect } from 'react';
import SwipeCard from './components/SwipeCard';
import GameStats from './components/GameStats';
import FeedbackModal from './components/FeedbackModal';
import { GameRound, GameState, FeedbackResponse, UserAnswer } from './types';
import './App.css';

const App: React.FC = () => {
  const [gameState, setGameState] = useState<GameState>({
    currentRound: null,
    score: 0,
    totalRounds: 0,
    gameComplete: false,
    roundsCompleted: 0,
    showFeedback: false
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  // Start new game
  const startGame = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/start-game', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const gameRound: GameRound = await response.json();
      setGameState({
        currentRound: gameRound,
        score: 0,
        totalRounds: 1,
        gameComplete: false,
        roundsCompleted: 0,
        showFeedback: false
      });
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
        score: feedback.is_correct ? prev.score + 1 : prev.score,
        totalRounds: prev.totalRounds + 1,
        showFeedback: true,
        lastFeedback: feedback,
        currentRound: feedback.next_round || null,
        gameComplete: !feedback.next_round,
        roundsCompleted: prev.roundsCompleted + 1
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
    startGame();
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

  if (error) {
    return (
      <div className="app">
        <div className="error">
          <h2>❌ Error</h2>
          <p>{error}</p>
          <button onClick={startGame} className="retry-btn">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🇫🇷 VocaTinder</h1>
        <p>Learn French gender with real news headlines!</p>
      </header>

      <GameStats gameState={gameState} />

      <main className="game-area">
        {gameState.showFeedback && gameState.lastFeedback ? (
          <FeedbackModal 
            feedback={gameState.lastFeedback}
            onContinue={handleContinue}
          />
        ) : gameState.currentRound ? (
          <SwipeCard 
            gameRound={gameState.currentRound}
            onSwipe={handleSwipe}
          />
        ) : (
          <div className="game-complete">
            <h2>🎉 Félicitations!</h2>
            <p>Ready to start learning?</p>
            <button onClick={startGame} className="play-again-btn">
              Start Game
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
