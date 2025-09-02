export interface GameRound {
  round_id: string;
  round_type: 'sentence_check' | 'word_check';
  display_text: string;
  target_word: string;
  correct_answer: boolean;
  options: {
    left: string;
    right: string;
  };
}

export interface UserAnswer {
  round_id: string;
  user_choice: 'left' | 'right';
}

export interface FeedbackResponse {
  is_correct: boolean;
  explanation: string;
  correct_answer: string;
  next_round?: GameRound;
}

export interface GameState {
  currentRound: GameRound | null;
  score: number;
  totalRounds: number;
  gameComplete: boolean;
  roundsCompleted: number;
  showFeedback: boolean;
  lastFeedback?: FeedbackResponse;
  languageLevel: LanguageLevel;
}

export type LanguageLevel = 'beginner' | 'intermediate' | 'advanced';

export type SwipeDirection = 'left' | 'right';
