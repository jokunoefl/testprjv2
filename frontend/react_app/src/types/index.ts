export interface PDF {
  id: number;
  url: string;
  school: string;
  subject: string;
  year: number;
  filename: string;
  created_at: string;
}

export interface PDFCreate {
  url: string;
  school: string;
  subject: string;
  year: number;
  filename: string;
}

export interface QuestionType {
  id: number;
  name: string;
  description?: string;
  created_at: string;
}

export interface QuestionTypeCreate {
  name: string;
  description?: string;
}

export interface Question {
  id: number;
  pdf_id: number;
  question_type_id: number;
  question_number: string;
  question_text: string;
  answer_text?: string;
  difficulty_level?: number;
  points?: number;
  page_number?: number;
  extracted_text?: string;
  keywords?: string;
  created_at: string;
}

export interface QuestionCreate {
  pdf_id: number;
  question_type_id: number;
  question_number: string;
  question_text: string;
  answer_text?: string;
  difficulty_level?: number;
  points?: number;
  page_number?: number;
  extracted_text?: string;
  keywords?: string;
}

export interface PDFWithQuestions extends PDF {
  questions: Question[];
} 