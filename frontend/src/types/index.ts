export interface Word {
  word: string;
  gender: 'masculine' | 'feminine';
  article: 'le' | 'la';
  translation?: string;
}

export interface ApiResponse {
  words: Word[];
}

export interface GameState {
  currentWordIndex: number;
  score: number;
  totalWords: number;
  gameComplete: boolean;
}

export type SwipeDirection = 'left' | 'right';
