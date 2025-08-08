import axios from 'axios';
import { PDF, Question, QuestionType, PDFWithQuestions } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001'; // 開発環境用

// デバッグ用ログ
console.log('API_BASE_URL:', API_BASE_URL);
console.log('Frontend connecting to Render backend...');

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
  
  viewPDF: (id: number): string => {
    const url = `${API_BASE_URL}/pdfs/${id}/view`;
    console.log('Generated PDF view URL:', url);
    console.log('API_BASE_URL:', API_BASE_URL);
    return url;
  },
  
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
    const maxRetries = 3;
    const baseTimeout = 180000; // 3分のタイムアウト
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`AI分析試行 ${attempt}/${maxRetries} for PDF ${pdfId}`);
        
        const response = await api.post<AIAnalysisResult>(`/pdfs/${pdfId}/analyze`, {}, {
          timeout: baseTimeout * attempt, // リトライごとにタイムアウトを延長
        });
        
        console.log(`AI分析成功: PDF ${pdfId}`);
        return response.data;
      } catch (error: any) {
        console.error(`AI分析試行 ${attempt} 失敗:`, error);
        
        // 最後の試行でない場合はリトライ
        if (attempt < maxRetries) {
          const waitTime = Math.min(1000 * attempt, 5000); // 1秒、2秒、5秒で待機
          console.log(`${waitTime}ms後にリトライします...`);
          await new Promise(resolve => setTimeout(resolve, waitTime));
          continue;
        }
        
        // 最後の試行でも失敗した場合
        console.error('AI分析が全ての試行で失敗しました');
        
        // エラーメッセージを改善
        let errorMessage = 'AI分析に失敗しました';
        if (error.response) {
          // サーバーからのエラーレスポンス
          const status = error.response.status;
          const data = error.response.data;
          
          if (status === 404) {
            errorMessage = 'PDFファイルが見つかりません';
          } else if (status === 500) {
            errorMessage = data?.error || 'サーバー内部エラーが発生しました';
          } else if (status === 408 || status === 504) {
            errorMessage = 'AI分析がタイムアウトしました。しばらくしてから再試行してください';
          } else {
            errorMessage = `サーバーエラー (${status}): ${data?.error || error.response.statusText}`;
          }
        } else if (error.code === 'ECONNABORTED') {
          errorMessage = 'AI分析がタイムアウトしました。しばらくしてから再試行してください';
        } else if (error.message) {
          errorMessage = `ネットワークエラー: ${error.message}`;
        }
        
        throw new Error(errorMessage);
      }
    }
    
    throw new Error('AI分析に失敗しました');
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