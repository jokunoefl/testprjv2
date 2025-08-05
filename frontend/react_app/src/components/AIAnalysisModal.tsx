import React from 'react';
import { AIAnalysisResult } from '../services/api';

interface AIAnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  result: AIAnalysisResult | null;
  loading: boolean;
  pdfName: string;
}

export const AIAnalysisModal: React.FC<AIAnalysisModalProps> = ({
  isOpen,
  onClose,
  result,
  loading,
  pdfName
}) => {
  if (!isOpen) return null;

  return (
    <div className="ai-analysis-modal-overlay" onClick={onClose}>
      <div className="ai-analysis-modal" onClick={(e) => e.stopPropagation()}>
        <div className="ai-analysis-modal-header">
          <h2>AI分析結果 - {pdfName}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="ai-analysis-modal-content">
          {loading && (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>AIがPDFを分析中です...</p>
              <p className="loading-note">この処理には数分かかる場合があります</p>
            </div>
          )}
          
          {!loading && result && (
            <div className="analysis-result">
              {result.success ? (
                <div>
                  <div className="analysis-info">
                    <p><strong>PDFファイルサイズ:</strong> {result.pdf_file_size} bytes</p>
                    <p><strong>変換ページ数:</strong> {result.pages_converted} ページ</p>
                  </div>
                  <div className="analysis-content">
                    <div dangerouslySetInnerHTML={{ __html: result.analysis?.replace(/\n/g, '<br>') || '' }} />
                  </div>
                </div>
              ) : (
                <div className="error-message">
                  <h3>分析に失敗しました</h3>
                  <p>{result.error}</p>
                  <div className="error-details">
                    <p>考えられる原因:</p>
                    <ul>
                      <li>PDFファイルが破損している</li>
                      <li>PDFファイルが大きすぎる</li>
                      <li>ネットワーク接続の問題</li>
                      <li>AI分析サービスの一時的な障害</li>
                    </ul>
                    <p>しばらく時間をおいてから再度お試しください。</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; 