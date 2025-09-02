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

  const handleKeyDown = (event: KeyboardEvent) => {
    if (disabled) return;
    
    if (event.key === 'ArrowUp') {
      event.preventDefault();
      const newIndex = currentIndex > 0 ? currentIndex - 1 : levels.length - 1;
      onLevelChange(levels[newIndex].value);
    } else if (event.key === 'ArrowDown') {
      event.preventDefault();
      const newIndex = currentIndex < levels.length - 1 ? currentIndex + 1 : 0;
      onLevelChange(levels[newIndex].value);
    }
  };

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, disabled]);

  return (
    <div className="level-selector">
      <h3>Choose Your Level</h3>
      <p className="keyboard-hint">Use ↑↓ arrow keys to navigate</p>
      <div className="level-options">
        {levels.map((level) => (
          <button
            key={level.value}
            className={`level-option ${selectedLevel === level.value ? 'selected' : ''}`}
            onClick={() => onLevelChange(level.value)}
            disabled={disabled}
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
