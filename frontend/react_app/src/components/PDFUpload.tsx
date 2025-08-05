import React, { useState } from 'react';
import { pdfApi } from '../services/api';

interface PDFUploadProps {
  onUploadSuccess?: () => void;
}

export const PDFUpload: React.FC<PDFUploadProps> = ({ onUploadSuccess = () => {} }) => {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState('');
  const [school, setSchool] = useState('');
  const [subject, setSubject] = useState('');
  const [year, setYear] = useState(new Date().getFullYear());
  const [isUploading, setIsUploading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isCrawling, setIsCrawling] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('ファイルを選択してください');
      return;
    }

    // ファイルサイズチェック（50MB制限）
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      setError('ファイルサイズが大きすぎます。50MB以下のファイルを選択してください。');
      return;
    }

    // ファイル形式チェック
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('PDFファイルのみアップロードできます。');
      return;
    }

    setIsUploading(true);
    setError('');
    setSuccess('');

    try {
      console.log('アップロード開始:', file.name, 'サイズ:', file.size);
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('url', url);
      formData.append('school', school);
      formData.append('subject', subject);
      formData.append('year', year.toString());

      console.log('FormData作成完了');
      const result = await pdfApi.uploadPDF(formData);
      console.log('アップロード成功:', result);
      
      setSuccess('PDFファイルをアップロードしました');
      onUploadSuccess();
      resetForm();
    } catch (err: any) {
      console.error('アップロードエラー:', err);
      
      let errorMessage = 'アップロードに失敗しました。';
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      } else if (err.code === 'NETWORK_ERROR') {
        errorMessage = 'ネットワーク接続エラーです。インターネット接続を確認してください。';
      } else if (err.code === 'TIMEOUT') {
        errorMessage = 'リクエストがタイムアウトしました。しばらく時間をおいて再試行してください。';
      }
      
      setError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const handleURLDownload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) {
      setError('URLを入力してください');
      return;
    }

    // URLの形式をチェック
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      setError('URLは http:// または https:// で始まる必要があります');
      return;
    }

    setIsDownloading(true);
    setError('');
    setSuccess('');

    try {
      console.log('URLダウンロード開始:', url);
      setSuccess('PDFファイルをダウンロードしています...');
      
      const result = await pdfApi.downloadPDF(url, school || undefined, subject || undefined, year);
      console.log('ダウンロード成功:', result);
      
      setSuccess('PDFファイルをダウンロードしました');
      onUploadSuccess();
      resetForm();
    } catch (err: any) {
      console.error('URLダウンロードエラー:', err);
      
      let errorMessage = 'ダウンロードに失敗しました。';
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      } else if (err.code === 'NETWORK_ERROR') {
        errorMessage = 'ネットワーク接続エラーです。インターネット接続を確認してください。';
      } else if (err.code === 'TIMEOUT') {
        errorMessage = 'リクエストがタイムアウトしました。しばらく時間をおいて再試行してください。';
      } else if (err.response?.status === 405) {
        errorMessage = 'Method Not Allowed: サーバーがこのリクエスト方法をサポートしていません。';
      } else if (err.response?.status === 404) {
        errorMessage = '指定されたURLのPDFファイルが見つかりません。';
      } else if (err.response?.status === 400) {
        errorMessage = 'リクエストが正しくありません。URLを確認してください。';
      }
      
      setError(errorMessage);
    } finally {
      setIsDownloading(false);
    }
  };

  const handleCrawlPDFs = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) {
      setError('URLを入力してください');
      return;
    }

    // URLの形式をチェック
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      setError('URLは http:// または https:// で始まる必要があります');
      return;
    }

    setIsCrawling(true);
    setError('');
    setSuccess('');

    try {
      setSuccess('クローリングを開始しています...');
      const result = await pdfApi.crawlPDFs(url, school || undefined, subject || undefined, year);
      
      if (result.successfully_saved > 0) {
        setSuccess(`${result.message} (${result.successfully_saved}/${result.total_found}個成功)`);
        if (result.failed_saves && result.failed_saves.length > 0) {
          console.warn('一部のPDFの保存に失敗:', result.failed_saves);
        }
      } else if (result.total_found > 0) {
        // PDFは見つかったが、保存に失敗した場合
        setError(`PDFファイルは見つかりましたが、保存に失敗しました。詳細: ${result.failed_saves?.join(', ') || '不明なエラー'}`);
      } else {
        // PDFが見つからなかった場合
        setError('このWebサイトにはPDFファイルが含まれていないか、アクセスできない形式です。別のURLを試してください。');
      }
      
      onUploadSuccess();
      resetForm();
    } catch (err: any) {
      console.error('クローリングエラー:', err);
      
      let errorMessage = 'クローリングに失敗しました。';
      
      if (err.response?.data?.detail) {
        // バックエンドから返される詳細なエラーメッセージ
        const detail = err.response.data.detail;
        if (detail.includes('PDFファイルが見つかりませんでした')) {
          errorMessage = 'このWebサイトにはPDFファイルが含まれていないか、アクセスできない形式です。別のURLを試してください。';
        } else if (detail.includes('タイムアウト')) {
          errorMessage = 'サイトへの接続がタイムアウトしました。サイトが応答していないか、ネットワーク接続に問題があります。';
        } else if (detail.includes('HTTPエラー')) {
          errorMessage = detail;
        } else if (detail.includes('リクエストエラー')) {
          errorMessage = detail;
        } else if (detail.includes('HTML解析エラー')) {
          errorMessage = 'サイトの構造が予期しない形式です。別のURLを試してください。';
        } else {
          errorMessage = detail;
        }
      } else if (err.message) {
        errorMessage = err.message;
      } else if (err.code === 'NETWORK_ERROR') {
        errorMessage = 'ネットワーク接続エラーです。インターネット接続を確認してください。';
      } else if (err.code === 'TIMEOUT') {
        errorMessage = 'リクエストがタイムアウトしました。しばらく時間をおいて再試行してください。';
      }
      
      setError(errorMessage);
    } finally {
      setIsCrawling(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setUrl('');
    setSchool('');
    setSubject('');
    setYear(new Date().getFullYear());
  };

  return (
    <div className="pdf-upload">
      <h2>PDFアップロード</h2>
      
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="upload-section">
        <h3>ファイルアップロード</h3>
        <form onSubmit={handleFileUpload}>
          <div>
            <label>PDFファイル:</label>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              required
            />
          </div>
          <div>
            <label>URL:</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/path/to/file.pdf"
            />
          </div>
          <div>
            <label>学校名:</label>
            <input
              type="text"
              value={school}
              onChange={(e) => setSchool(e.target.value)}
              placeholder="東京中学校"
              required
            />
          </div>
          <div>
            <label>科目:</label>
            <select value={subject} onChange={(e) => setSubject(e.target.value)} required>
              <option value="">選択してください</option>
              <option value="math">算数</option>
              <option value="japanese">国語</option>
              <option value="science">理科</option>
              <option value="social">社会</option>
            </select>
          </div>
          <div>
            <label>年度:</label>
            <input
              type="number"
              value={year}
              onChange={(e) => setYear(parseInt(e.target.value))}
              min="2000"
              max="2030"
              required
            />
          </div>
          <button type="submit" disabled={isUploading}>
            {isUploading ? 'アップロード中...' : 'アップロード'}
          </button>
        </form>
      </div>

      <div className="download-section">
        <h3>URLからダウンロード</h3>
        <form onSubmit={handleURLDownload}>
          <div>
            <label>PDF URL:</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/path/to/file.pdf"
              required
            />
          </div>
          <div>
            <label>学校名 (オプション):</label>
            <input
              type="text"
              value={school}
              onChange={(e) => setSchool(e.target.value)}
              placeholder="自動抽出されます"
            />
          </div>
          <div>
            <label>科目 (オプション):</label>
            <select value={subject} onChange={(e) => setSubject(e.target.value)}>
              <option value="">自動抽出されます</option>
              <option value="math">算数</option>
              <option value="japanese">国語</option>
              <option value="science">理科</option>
              <option value="social">社会</option>
            </select>
          </div>
          <div>
            <label>年度 (オプション):</label>
            <input
              type="number"
              value={year}
              onChange={(e) => setYear(parseInt(e.target.value))}
              min="2000"
              max="2030"
            />
          </div>
          <button type="submit" disabled={isDownloading}>
            {isDownloading ? 'ダウンロード中...' : 'ダウンロード'}
          </button>
        </form>
      </div>

      <div className="crawl-section">
        <h3>WebサイトからPDFを自動抽出</h3>
        <form onSubmit={handleCrawlPDFs}>
          <div>
            <label>Webサイト URL:</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/past-exams"
              required
            />
          </div>
          <div>
            <label>学校名 (オプション):</label>
            <input
              type="text"
              value={school}
              onChange={(e) => setSchool(e.target.value)}
              placeholder="自動抽出されます"
            />
          </div>
          <div>
            <label>科目 (オプション):</label>
            <select value={subject} onChange={(e) => setSubject(e.target.value)}>
              <option value="">自動抽出されます</option>
              <option value="math">算数</option>
              <option value="japanese">国語</option>
              <option value="science">理科</option>
              <option value="social">社会</option>
            </select>
          </div>
          <div>
            <label>年度 (オプション):</label>
            <input
              type="number"
              value={year}
              onChange={(e) => setYear(parseInt(e.target.value))}
              min="2000"
              max="2030"
            />
          </div>
          <button type="submit" disabled={isCrawling}>
            {isCrawling ? 'クローリング中...' : 'PDFを自動抽出'}
          </button>
        </form>
      </div>
    </div>
  );
}; 