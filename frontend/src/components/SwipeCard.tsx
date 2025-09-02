import React, { useEffect, useRef } from 'react';
import { GameRound } from '../types';

interface SwipeCardProps {
  gameRound: GameRound;
  onSwipe: (direction: 'left' | 'right') => void;
}

const SwipeCard: React.FC<SwipeCardProps> = ({ gameRound, onSwipe }) => {
  const isWordCheck = gameRound.round_type === 'word_check';
  const cardRef = useRef<HTMLDivElement>(null);
  const startX = useRef<number>(0);
  const currentX = useRef<number>(0);
  const isDragging = useRef<boolean>(false);
  
  // Touch/Mouse event handlers
  const handleStart = (clientX: number) => {
    startX.current = clientX;
    currentX.current = clientX;
    isDragging.current = true;
    if (cardRef.current) {
      cardRef.current.style.transition = 'none';
    }
  };

  const handleMove = (clientX: number) => {
    if (!isDragging.current || !cardRef.current) return;
    
    currentX.current = clientX;
    const deltaX = currentX.current - startX.current;
    const rotation = deltaX * 0.1;
    
    cardRef.current.style.transform = `translateX(${deltaX}px) rotate(${rotation}deg)`;
    cardRef.current.style.opacity = String(Math.max(0.5, 1 - Math.abs(deltaX) / 300));
  };

  const handleEnd = () => {
    if (!isDragging.current || !cardRef.current) return;
    
    const deltaX = currentX.current - startX.current;
    const threshold = 100;
    
    if (Math.abs(deltaX) > threshold) {
      // Swipe detected
      const direction = deltaX > 0 ? 'right' : 'left';
      
      // Animate card exit
      cardRef.current.style.transition = 'transform 0.3s ease-out, opacity 0.3s ease-out';
      cardRef.current.style.transform = `translateX(${deltaX > 0 ? 300 : -300}px) rotate(${deltaX > 0 ? 30 : -30}deg)`;
      cardRef.current.style.opacity = '0';
      
      setTimeout(() => onSwipe(direction), 300);
    } else {
      // Snap back to center
      cardRef.current.style.transition = 'transform 0.3s ease-out, opacity 0.3s ease-out';
      cardRef.current.style.transform = 'translateX(0px) rotate(0deg)';
      cardRef.current.style.opacity = '1';
    }
    
    isDragging.current = false;
  };

  // Touch events
  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault();
    handleStart(e.touches[0].clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    e.preventDefault();
    handleMove(e.touches[0].clientX);
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault();
    handleEnd();
  };

  // Mouse events
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    handleStart(e.clientX);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    handleMove(e.clientX);
  };

  const handleMouseUp = (e: React.MouseEvent) => {
    e.preventDefault();
    handleEnd();
  };

  // Keyboard support
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'ArrowLeft') {
        onSwipe('left');
      } else if (event.key === 'ArrowRight') {
        onSwipe('right');
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [onSwipe]);

  // Mouse move/up events on document for smooth dragging
  useEffect(() => {
    const handleDocumentMouseMove = (e: MouseEvent) => {
      if (isDragging.current) {
        handleMove(e.clientX);
      }
    };

    const handleDocumentMouseUp = () => {
      if (isDragging.current) {
        handleEnd();
      }
    };

    document.addEventListener('mousemove', handleDocumentMouseMove);
    document.addEventListener('mouseup', handleDocumentMouseUp);
    
    return () => {
      document.removeEventListener('mousemove', handleDocumentMouseMove);
      document.removeEventListener('mouseup', handleDocumentMouseUp);
    };
  }, [handleEnd]);

  return (
    <div className="swipe-container">
      <div 
        ref={cardRef}
        className="swipe-card"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
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
      
        <div className="swipe-indicators">
          <div className="swipe-hint left-hint">
            <span className="arrow">👈</span>
            <span className="label">{gameRound.options.left}</span>
          </div>
          <div className="swipe-hint right-hint">
            <span className="arrow">👉</span>
            <span className="label">{gameRound.options.right}</span>
          </div>
        </div>
        
        <div className="keyboard-hint">
          <span>💻 Use ← → arrow keys or swipe on mobile</span>
        </div>
      </div>
    </div>
  );
};

export default SwipeCard;
