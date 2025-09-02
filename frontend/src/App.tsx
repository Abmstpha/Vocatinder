import React, { useState, useEffect } from 'react';
import SwipeCard from './components/SwipeCard';
import GameStats from './components/GameStats';
import { Word, GameState, ApiResponse } from './types';
import './App.css';

const App: React.FC = () => {
  const [words, setWords] = useState<Word[]>([]);
  const [gameState, setGameState] = useState<GameState>({
    currentWordIndex: 0,
    score: 0,
    totalWords: 0,
    gameComplete: false
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  // Fetch words from FastAPI backend
  const fetchWords = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/generate-words', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ApiResponse = await response.json();
      setWords(data.words);
      setGameState({
        currentWordIndex: 0,
        score: 0,
        totalWords: data.words.length,
        gameComplete: false
      });
      setError('');
    } catch (err) {
      setError('Failed to fetch words. Make sure the backend is running!');
      console.error('Error fetching words:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle swipe action
  const handleSwipe = (direction: 'left' | 'right') => {
    const currentWord = words[gameState.currentWordIndex];
    const isCorrect = 
      (direction === 'left' && currentWord.gender === 'feminine') ||
      (direction === 'right' && currentWord.gender === 'masculine');

    const newScore = isCorrect ? gameState.score + 1 : gameState.score;
    const nextIndex = gameState.currentWordIndex + 1;
    const isGameComplete = nextIndex >= gameState.totalWords;

    setGameState({
      currentWordIndex: nextIndex,
      score: newScore,
      totalWords: gameState.totalWords,
      gameComplete: isGameComplete
    });
  };

  // Reset game
  const resetGame = () => {
    fetchWords();
  };

  useEffect(() => {
    fetchWords();
  }, []);

  if (loading) {
    return (
      <div className="app">
        <div className="loading">
          <h2>🇫🇷 Loading French words...</h2>
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
          <button onClick={fetchWords} className="retry-btn">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🇫🇷 Vocatinder</h1>
        <p>Swipe to learn French gender!</p>
      </header>

      <GameStats gameState={gameState} />

      <main className="game-area">
        {!gameState.gameComplete && words.length > 0 ? (
          <SwipeCard 
            word={words[gameState.currentWordIndex]}
            onSwipe={handleSwipe}
          />
        ) : (
          <div className="game-complete">
            <h2>🎉 Félicitations!</h2>
            <p>You completed the game!</p>
            <button onClick={resetGame} className="play-again-btn">
              Play Again
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
