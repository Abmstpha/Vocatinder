import React from 'react';
import { GameState } from '../types';

interface GameStatsProps {
  gameState: GameState;
}

const GameStats: React.FC<GameStatsProps> = ({ gameState }) => {
  const { score, totalRounds, gameComplete, roundsCompleted } = gameState;
  const accuracy = roundsCompleted > 0 ? Math.round((score / roundsCompleted) * 100) : 0;

  return (
    <div className="game-stats">
      <div className="stats-row">
        <div className="stat">
          <span className="stat-label">Progress</span>
          <span className="stat-value">{roundsCompleted}/{totalRounds}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Score</span>
          <span className="stat-value">{score}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Accuracy</span>
          <span className="stat-value">{accuracy}%</span>
        </div>
      </div>
      
      {gameComplete && (
        <div className="game-complete">
          <h2>🎉 Game Complete!</h2>
          <p>Final Score: {score}/{totalRounds} ({accuracy}%)</p>
        </div>
      )}
    </div>
  );
};

export default GameStats;
