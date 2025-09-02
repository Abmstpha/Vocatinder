import React from 'react';
import { FeedbackResponse } from '../types';

interface FeedbackModalProps {
  feedback: FeedbackResponse;
  onContinue: () => void;
}

const FeedbackModal: React.FC<FeedbackModalProps> = ({ feedback, onContinue }) => {
  return (
    <div className="feedback-modal">
      <div className="feedback-content">
        <div className={`feedback-result ${feedback.is_correct ? 'correct' : 'incorrect'}`}>
          {feedback.is_correct ? '✅ Correct!' : '❌ Incorrect'}
        </div>
        
        <div className="feedback-explanation">
          <p>{feedback.explanation}</p>
        </div>
        
        <div className="correct-answer">
          <strong>Correct answer:</strong> {feedback.correct_answer}
        </div>
        
        <button className="continue-btn" onClick={onContinue}>
          {feedback.next_round ? 'Continue to Next Round' : 'Start New Game'}
        </button>
      </div>
    </div>
  );
};

export default FeedbackModal;
