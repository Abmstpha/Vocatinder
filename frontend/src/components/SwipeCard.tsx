import React from 'react';
import { Word } from '../types';

interface SwipeCardProps {
  word: Word;
  onSwipe: (direction: 'left' | 'right') => void;
}

const SwipeCard: React.FC<SwipeCardProps> = ({ word, onSwipe }) => {
  return (
    <div className="swipe-card">
      <div className="card-content">
        <h1 className="french-word">{word.word}</h1>
        {word.translation && (
          <p className="translation">{word.translation}</p>
        )}
      </div>
      
      <div className="swipe-buttons">
        <button 
          className="swipe-btn feminine"
          onClick={() => onSwipe('left')}
        >
          👈 LA (Feminine)
        </button>
        <button 
          className="swipe-btn masculine"
          onClick={() => onSwipe('right')}
        >
          LE (Masculine) 👉
        </button>
      </div>
      
      <div className="swipe-hints">
        <span className="hint-left">Swipe left for LA</span>
        <span className="hint-right">Swipe right for LE</span>
      </div>
    </div>
  );
};

export default SwipeCard;
