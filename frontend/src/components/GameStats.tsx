import React from 'react';
import { GameState } from '../types';

interface GameStatsProps {
  gameState: GameState;
}

const GameStats: React.FC<GameStatsProps> = ({ gameState }) => {
  const { score, totalRounds, gameComplete, currentRound } = gameState;
  const accuracy = totalRounds > 0 ? Math.round((score / totalRounds) * 100) : 0;
  const roundType = currentRound?.round_type === 'word_check' ? 'Round 2' : 'Round 1';

  return (
    <div className="game-stats">
      <div className="stats-row">
        <div className="stat">
          <span className="stat-label">Score</span>
          <span className="stat-value">{score}/{totalRounds}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Current</span>
          <span className="stat-value">{currentRound ? roundType : 'Ready'}</span>
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
