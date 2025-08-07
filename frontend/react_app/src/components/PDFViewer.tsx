import React, { useState, useEffect, useRef } from 'react';
import { PDF } from '../types';
import { pdfApi } from '../services/api';

interface PDFViewerProps {
  pdfId: number;
  onBack: () => void;
}

export const PDFViewer: React.FC<PDFViewerProps> = ({ pdfId, onBack }) => {
  const [pdf, setPdf] = useState<PDF | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pdfUrl, setPdfUrl] = useState('');
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const loadPDF = async () => {
      try {
        setLoading(true);
        setError('');
        console.log('Loading PDF with ID:', pdfId);
        
        const data = await pdfApi.getPDF(pdfId);
        console.log('PDF data loaded:', data);
        setPdf(data);
        
        const url = pdfApi.viewPDF(pdfId);
        console.log('PDF URL generated:', url);
        setPdfUrl(url);
        
        console.log('PDF loading completed successfully');
      } catch (err: any) {
        console.error('PDF loading error:', err);
        setError(`PDFの読み込みに失敗しました: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    loadPDF();
  }, [pdfId]);

  const getSubjectLabel = (subject: string) => {
    const labels: { [key: string]: string } = {
      'math': '算数',
      'japanese': '国語',
      'science': '理科',
      'social': '社会',
      'unknown': '不明'
    };
    return labels[subject] || subject;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP');
  };

  const handleDownloadPDF = () => {
    if (pdfUrl && pdf) {
      console.log('Downloading PDF:', pdfUrl, 'as', pdf.filename);
      try {
        const link = document.createElement('a');
        link.href = pdfUrl;
        link.download = pdf.filename;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        console.log('PDF download initiated');
      } catch (error) {
        console.error('Error downloading PDF:', error);
        alert('PDFのダウンロードに失敗しました。');
      }
    } else {
      alert('PDFのダウンロードに必要な情報が不足しています。');
    }
  };

  if (loading) {
    return (
      <div className="pdf-viewer">
        <div className="pdf-viewer-header">
          <button onClick={onBack} className="back-button">
            ← 過去問題一覧に戻る
          </button>
        </div>
        <div className="pdf-viewer-loading">読み込み中...</div>
      </div>
    );
  }

  if (error || !pdf) {
    return (
      <div className="pdf-viewer">
        <div className="pdf-viewer-header">
          <button onClick={onBack} className="back-button">
            ← 過去問題一覧に戻る
          </button>
        </div>
        <div className="pdf-viewer-error">
          <div className="error">{error || 'PDFが見つかりません'}</div>
          <button onClick={onBack}>過去問題一覧に戻る</button>
        </div>
      </div>
    );
  }

  return (
    <div className="pdf-viewer">
      <div className="pdf-viewer-header">
        <button onClick={onBack} className="back-button">
          ← 過去問題一覧に戻る
        </button>
        <h1>{pdf.school} - {getSubjectLabel(pdf.subject)} ({pdf.year})</h1>
      </div>

      <div className="pdf-info">
        <div className="pdf-metadata">
          <p><strong>学校名:</strong> {pdf.school}</p>
          <p><strong>科目:</strong> {getSubjectLabel(pdf.subject)}</p>
          <p><strong>年度:</strong> {pdf.year}</p>
          <p><strong>ファイル名:</strong> {pdf.filename}</p>
          <p><strong>登録日:</strong> {formatDate(pdf.created_at)}</p>
          <p><strong>URL:</strong> <a href={pdf.url} target="_blank" rel="noopener noreferrer">{pdf.url}</a></p>
          <p><strong>PDF表示URL:</strong> <a href={pdfUrl} target="_blank" rel="noopener noreferrer">{pdfUrl}</a></p>
          <p><strong>PDF ID:</strong> {pdfId}</p>
        </div>
      </div>

      <div className="pdf-content">
        <div className="pdf-controls">
          <button 
            onClick={handleDownloadPDF}
            className="pdf-download-btn"
          >
            💾 PDFをダウンロード
          </button>
        </div>
        
        <div className="pdf-embedded-view">
          <iframe
            src={pdfUrl}
            title={`${pdf.school} - ${getSubjectLabel(pdf.subject)} (${pdf.year})`}
            width="100%"
            height="800px"
            style={{ border: '1px solid #ccc' }}
            onLoad={() => {
              console.log('PDF iframe loaded successfully');
            }}
            onError={(e) => {
              console.error('PDF iframe error:', e);
              alert('PDFの埋め込み表示に失敗しました。');
            }}
          />
        </div>
      </div>
    </div>
  );
}; 