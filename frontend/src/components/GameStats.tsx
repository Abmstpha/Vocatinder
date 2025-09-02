import React from 'react';
import { GameState } from '../types';

interface GameStatsProps {
  gameState: GameState;
}

const GameStats: React.FC<GameStatsProps> = ({ gameState }) => {
  const { currentWordIndex, score, totalWords, gameComplete } = gameState;
  const accuracy = totalWords > 0 ? Math.round((score / totalWords) * 100) : 0;

  return (
    <div className="game-stats">
      <div className="stats-row">
        <div className="stat">
          <span className="stat-label">Score</span>
          <span className="stat-value">{score}/{totalWords}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Progress</span>
          <span className="stat-value">{currentWordIndex + 1}/{totalWords}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Accuracy</span>
          <span className="stat-value">{accuracy}%</span>
        </div>
      </div>
      
      {gameComplete && (
        <div className="game-complete">
          <h2>🎉 Game Complete!</h2>
          <p>Final Score: {score}/{totalWords} ({accuracy}%)</p>
        </div>
      )}
    </div>
  );
};

export default GameStats;
