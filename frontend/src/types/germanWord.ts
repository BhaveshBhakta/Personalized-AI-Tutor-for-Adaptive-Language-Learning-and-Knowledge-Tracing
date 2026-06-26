export interface GermanWord {
  id: number;
  word: string;
  article?: string;
  plural?: string;
  translation: string;
  category: string;
  difficulty: number;
  frequency_rank: number;
}