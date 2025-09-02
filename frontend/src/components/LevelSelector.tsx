import React, { useEffect } from 'react';
import { LanguageLevel } from '../types';
import './LevelSelector.css';

interface LevelSelectorProps {
  selectedLevel: LanguageLevel;
  onLevelChange: (level: LanguageLevel) => void;
  disabled?: boolean;
}

const LevelSelector: React.FC<LevelSelectorProps> = ({ 
  selectedLevel, 
  onLevelChange, 
  disabled = false 
}) => {
  const levels: { value: LanguageLevel; label: string; description: string }[] = [
    {
      value: 'beginner',
      label: '🌱 Beginner',
      description: 'Simple words, basic articles'
    },
    {
      value: 'intermediate',
      label: '📚 Intermediate', 
      description: 'Common vocabulary, varied structures'
    },
    {
      value: 'advanced',
      label: '🎓 Advanced',
      description: 'Complex words, nuanced grammar'
    }
  ];

  const currentIndex = levels.findIndex(level => level.value === selectedLevel);

  const containerRef = React.useRef<HTMLDivElement>(null);

  const handleContainerKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (disabled) return;
    
    if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
      event.preventDefault();
      event.stopPropagation();
      
      if (event.key === 'ArrowUp') {
        const newIndex = currentIndex > 0 ? currentIndex - 1 : levels.length - 1;
        onLevelChange(levels[newIndex].value);
      } else if (event.key === 'ArrowDown') {
        const newIndex = currentIndex < levels.length - 1 ? currentIndex + 1 : 0;
        onLevelChange(levels[newIndex].value);
      }
    }
  };

  const handleButtonKeyDown = (event: React.KeyboardEvent) => {
    // Completely block all arrow keys on buttons
    if (event.key === 'ArrowUp' || event.key === 'ArrowDown' || event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      event.stopPropagation();
    }
  };

  // Focus the container when component mounts so it can receive keyboard events
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.focus();
    }
  }, []);

  return (
    <div 
      className="level-selector"
      ref={containerRef}
      onKeyDown={handleContainerKeyDown}
      tabIndex={0}
    >
      <h3>Choose Your Level</h3>
      <p className="keyboard-hint">Use ↑↓ arrow keys to navigate</p>
      <div className="level-options">
        {levels.map((level) => (
          <button
            key={level.value}
            className={`level-option ${selectedLevel === level.value ? 'selected' : ''}`}
            onClick={() => onLevelChange(level.value)}
            onKeyDown={handleButtonKeyDown}
            disabled={disabled}
            tabIndex={-1}
          >
            <div className="level-label">{level.label}</div>
            <div className="level-description">{level.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default LevelSelector;
