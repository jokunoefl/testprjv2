import axios from 'axios';
import { PDF, Question, QuestionType, PDFWithQuestions } from '../types';

const API_BASE_URL = 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60秒のタイムアウト（AI分析用に延長）
});

// リクエストインターセプター
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// レスポンスインターセプター
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    });
    return Promise.reject(error);
  }
);

interface CrawlResult {
  message: string;
  total_found: number;
  successfully_saved: number;
  failed_saves?: string[];
}

export interface AIAnalysisResult {
  success: boolean;
  analysis?: string;
  error?: string;
  extracted_text_length?: number;
  pdf_file_size?: number;
  pages_converted?: number;
}

export const pdfApi = {
  getPDFs: async (): Promise<PDF[]> => {
    try {
      console.log('Fetching PDFs from:', `${API_BASE_URL}/pdfs/`);
      const response = await api.get<PDF[]>('/pdfs/');
      console.log('PDFs fetched successfully:', response.data.length, 'items');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch PDFs:', error);
      throw error;
    }
  },
  
  getPDF: async (id: number): Promise<PDF> => {
    try {
      const response = await api.get<PDF>(`/pdfs/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch PDF ${id}:`, error);
      throw error;
    }
  },
  
  updatePDF: async (id: number, pdfUpdate: Partial<PDF>): Promise<PDF> => {
    try {
      const response = await api.put<PDF>(`/pdfs/${id}`, pdfUpdate);
      return response.data;
    } catch (error) {
      console.error(`Failed to update PDF ${id}:`, error);
      throw error;
    }
  },
  
  uploadPDF: async (formData: FormData): Promise<PDF> => {
    try {
      const response = await api.post<PDF>('/upload_pdf/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Failed to upload PDF:', error);
      throw error;
    }
  },
  
  downloadPDF: async (url: string, school?: string, subject?: string, year?: number): Promise<PDF> => {
    try {
      const formData = new FormData();
      formData.append('url', url);
      if (school) formData.append('school', school);
      if (subject) formData.append('subject', subject);
      if (year) formData.append('year', year.toString());
      
      const response = await api.post<PDF>('/download_pdf/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Failed to download PDF:', error);
      throw error;
    }
  },
  
  crawlPDFs: async (url: string, school?: string, subject?: string, year?: number): Promise<CrawlResult> => {
    try {
      const formData = new FormData();
      formData.append('url', url);
      if (school) formData.append('school', school);
      if (subject) formData.append('subject', subject);
      if (year) formData.append('year', year.toString());
      
      const response = await api.post<CrawlResult>('/crawl_pdfs/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Failed to crawl PDFs:', error);
      throw error;
    }
  },
  
  viewPDF: (id: number): string => `${API_BASE_URL}/pdfs/${id}/view`,
  
  getPDFWithQuestions: async (id: number): Promise<PDFWithQuestions> => {
    try {
      const response = await api.get<PDFWithQuestions>(`/pdfs/${id}/with-questions`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch PDF with questions ${id}:`, error);
      throw error;
    }
  },

  analyzePDF: async (pdfId: number): Promise<AIAnalysisResult> => {
    try {
      const response = await api.post<AIAnalysisResult>(`/pdfs/${pdfId}/analyze`, {}, {
        timeout: 120000, // AI分析用に2分のタイムアウト
      });
      return response.data;
    } catch (error) {
      console.error('Failed to analyze PDF:', error);
      throw error;
    }
  },
};

export const questionTypeApi = {
  // 問題タイプ一覧を取得
  getQuestionTypes: async (): Promise<QuestionType[]> => {
    const response = await api.get<QuestionType[]>('/question-types/');
    return response.data;
  },

  // 特定の問題タイプを取得
  getQuestionType: async (questionTypeId: number): Promise<QuestionType> => {
    const response = await api.get<QuestionType>(`/question-types/${questionTypeId}`);
    return response.data;
  },

  // 問題タイプを作成
  createQuestionType: async (questionType: Partial<QuestionType>): Promise<QuestionType> => {
    const response = await api.post<QuestionType>('/question-types/', questionType);
    return response.data;
  },
};

export const questionApi = {
  // 問題一覧を取得
  getQuestions: async (): Promise<Question[]> => {
    const response = await api.get<Question[]>('/questions/');
    return response.data;
  },

  // 特定の問題を取得
  getQuestion: async (questionId: number): Promise<Question> => {
    const response = await api.get<Question>(`/questions/${questionId}`);
    return response.data;
  },

  // PDFに関連する問題一覧を取得
  getQuestionsByPDF: async (pdfId: number): Promise<Question[]> => {
    const response = await api.get<Question[]>(`/pdfs/${pdfId}/questions`);
    return response.data;
  },

  // 問題を作成
  createQuestion: async (question: Partial<Question>): Promise<Question> => {
    const response = await api.post<Question>('/questions/', question);
    return response.data;
  },

  // 問題を更新
  updateQuestion: async (questionId: number, questionUpdate: Partial<Question>): Promise<Question> => {
    const response = await api.put<Question>(`/questions/${questionId}`, questionUpdate);
    return response.data;
  },

  // 問題を削除
  deleteQuestion: async (questionId: number): Promise<any> => {
    const response = await api.delete(`/questions/${questionId}`);
    return response.data;
  },
}; 