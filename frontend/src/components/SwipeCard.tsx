import React from 'react';
import { GameRound } from '../types';

interface SwipeCardProps {
  gameRound: GameRound;
  onSwipe: (direction: 'left' | 'right') => void;
}

const SwipeCard: React.FC<SwipeCardProps> = ({ gameRound, onSwipe }) => {
  const isWordCheck = gameRound.round_type === 'word_check';
  
  return (
    <div className="swipe-card">
      <div className="card-content">
        <div className="round-type">
          {gameRound.round_type === 'sentence_check' ? '📝 Round 1: Grammar Check' : '🎯 Round 2: Gender Check'}
        </div>
        
        {isWordCheck ? (
          <h1 className="french-word">{gameRound.display_text}</h1>
        ) : (
          <div className="sentence-display">
            <p className="french-sentence">{gameRound.display_text}</p>
            <p className="target-word">Target word: <strong>{gameRound.target_word}</strong></p>
          </div>
        )}
      </div>
      
      <div className="swipe-buttons">
        <button 
          className="swipe-btn left-option"
          onClick={() => onSwipe('left')}
        >
          👈 {gameRound.options.left}
        </button>
        <button 
          className="swipe-btn right-option"
          onClick={() => onSwipe('right')}
        >
          {gameRound.options.right} 👉
        </button>
      </div>
      
      <div className="swipe-hints">
        <span className="hint-left">{gameRound.options.left}</span>
        <span className="hint-right">{gameRound.options.right}</span>
      </div>
    </div>
  );
};

export default SwipeCard;
