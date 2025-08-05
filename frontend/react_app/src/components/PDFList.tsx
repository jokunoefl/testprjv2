import React, { useState, useEffect } from 'react';
import { PDF } from '../types';
import { pdfApi, AIAnalysisResult } from '../services/api';
import { AIAnalysisModal } from './AIAnalysisModal';

interface PDFListProps {
  onPDFSelect?: (pdfId: number) => void;
  onQuestionManage?: (pdf: PDF) => void;
  showAdminControls?: boolean;
}

export const PDFList: React.FC<PDFListProps> = ({ 
  onPDFSelect = () => {}, 
  onQuestionManage = () => {},
  showAdminControls = false
}) => {
  const [pdfs, setPdfs] = useState<PDF[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSubject, setFilterSubject] = useState('');
  const [filterYear, setFilterYear] = useState('');
  const [expandedSchools, setExpandedSchools] = useState<Set<string>>(new Set());
  const [expandedYears, setExpandedYears] = useState<Set<string>>(new Set());
  
  // AI分析関連の状態
  const [aiAnalysisModalOpen, setAiAnalysisModalOpen] = useState(false);
  const [aiAnalysisLoading, setAiAnalysisLoading] = useState(false);
  const [aiAnalysisResult, setAiAnalysisResult] = useState<AIAnalysisResult | null>(null);
  const [selectedPdfForAnalysis, setSelectedPdfForAnalysis] = useState<PDF | null>(null);

  const loadPDFs = async () => {
    try {
      setLoading(true);
      setError('');
      console.log('Loading PDFs...');
      const data = await pdfApi.getPDFs();
      console.log('PDFs loaded:', data.length, 'items');
      setPdfs(data);
    } catch (err: any) {
      console.error('Error loading PDFs:', err);
      let errorMessage = '過去問題一覧の取得に失敗しました';
      
      if (err.response) {
        // サーバーからのエラーレスポンス
        errorMessage = `サーバーエラー: ${err.response.status} - ${err.response.statusText}`;
        if (err.response.data && err.response.data.detail) {
          errorMessage += ` (${err.response.data.detail})`;
        }
      } else if (err.request) {
        // リクエストは送信されたがレスポンスがない
        errorMessage = 'サーバーに接続できません。バックエンドが起動しているか確認してください。';
      } else {
        // その他のエラー
        errorMessage = `エラー: ${err.message}`;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPDFs();
  }, []);

  const filteredPDFs = pdfs.filter(pdf => {
    const matchesSearch = pdf.school.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         pdf.filename.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSubject = !filterSubject || pdf.subject === filterSubject;
    const matchesYear = !filterYear || pdf.year.toString() === filterYear;
    
    return matchesSearch && matchesSubject && matchesYear;
  });

  // 学校→年度→PDFの階層構造でグルーピング
  const groupedPDFs = filteredPDFs.reduce((groups, pdf) => {
    const school = pdf.school;
    const year = pdf.year || '不明'; // 年度が不明な場合は「不明」として扱う
    
    if (!groups[school]) {
      groups[school] = {};
    }
    if (!groups[school][year]) {
      groups[school][year] = [];
    }
    groups[school][year].push(pdf);
    return groups;
  }, {} as { [key: string]: { [key: string]: typeof filteredPDFs } });

  // 学校名でソート
  const sortedSchools = Object.keys(groupedPDFs).sort();

  // 学校の統計情報を取得
  const getSchoolStats = (schoolPDFs: { [key: string]: typeof filteredPDFs }) => {
    const allPDFs = Object.values(schoolPDFs).flat();
    const totalPDFs = allPDFs.length;
    const subjects = new Set(allPDFs.map(pdf => pdf.subject));
    const years = new Set(allPDFs.map(pdf => pdf.year));
    
    return {
      totalPDFs,
      subjectCount: subjects.size,
      yearCount: years.size,
      subjects: Array.from(subjects).map(subject => getSubjectLabel(subject)).join(', '),
      yearRange: `${Math.min(...Array.from(years))} - ${Math.max(...Array.from(years))}`
    };
  };

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



  const handlePDFClick = (pdfId: number) => {
    onPDFSelect(pdfId);
  };

  const handleQuestionManage = (pdfId: number) => {
    const pdf = pdfs.find(pdf => pdf.id === pdfId);
    if (pdf) {
      onQuestionManage(pdf);
    }
  };

  const toggleSchoolExpansion = (school: string) => {
    const newExpandedSchools = new Set(expandedSchools);
    if (newExpandedSchools.has(school)) {
      newExpandedSchools.delete(school);
    } else {
      newExpandedSchools.add(school);
    }
    setExpandedSchools(newExpandedSchools);
  };

  const toggleYearExpansion = (school: string, year: string) => {
    const key = `${school}-${year}`;
    const newExpandedYears = new Set(expandedYears);
    if (newExpandedYears.has(key)) {
      newExpandedYears.delete(key);
    } else {
      newExpandedYears.add(key);
    }
    setExpandedYears(newExpandedYears);
  };

  const handleAIAnalysis = async (pdf: PDF) => {
    setSelectedPdfForAnalysis(pdf);
    setAiAnalysisModalOpen(true);
    setAiAnalysisLoading(true);
    setAiAnalysisResult(null);

    try {
      console.log(`AI分析開始: PDF ID ${pdf.id} (${pdf.filename})`);
      const result = await pdfApi.analyzePDF(pdf.id);
      console.log('AI分析結果:', result);
      setAiAnalysisResult(result);
    } catch (error: any) {
      console.error('AI分析エラー:', error);
      let errorMessage = 'AI分析中にエラーが発生しました。';
      
      if (error.response) {
        // サーバーからのエラーレスポンス
        if (error.response.data && error.response.data.error) {
          errorMessage = error.response.data.error;
        } else {
          errorMessage = `サーバーエラー: ${error.response.status} - ${error.response.statusText}`;
        }
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'AI分析がタイムアウトしました。PDFが大きすぎる可能性があります。';
      } else if (error.message) {
        errorMessage = `エラー: ${error.message}`;
      }
      
      setAiAnalysisResult({
        success: false,
        error: errorMessage
      });
    } finally {
      setAiAnalysisLoading(false);
    }
  };

  const closeAIAnalysisModal = () => {
    setAiAnalysisModalOpen(false);
    setAiAnalysisLoading(false);
    setAiAnalysisResult(null);
    setSelectedPdfForAnalysis(null);
  };

  if (loading) {
    return <div>読み込み中...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <>
      <div className="pdf-list">
        <h2>過去問題一覧</h2>
        
        <div className="filters">
          <div>
            <label>検索:</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="学校名またはファイル名で検索"
            />
          </div>
          <div>
            <label>科目:</label>
            <select value={filterSubject} onChange={(e) => setFilterSubject(e.target.value)}>
              <option value="">すべて</option>
              <option value="math">算数</option>
              <option value="japanese">国語</option>
              <option value="science">理科</option>
              <option value="social">社会</option>
            </select>
          </div>
          <div>
            <label>年度:</label>
            <select value={filterYear} onChange={(e) => setFilterYear(e.target.value)}>
              <option value="">すべて</option>
              {Array.from(new Set(pdfs.map(pdf => pdf.year))).sort().reverse().map(year => (
                <option key={year} value={year.toString()}>{year}</option>
              ))}
            </select>
          </div>
        </div>

        {sortedSchools.length === 0 ? (
          <div className="no-results">過去問題が見つかりません</div>
        ) : (
          <div className="pdf-grid">
            {sortedSchools.map(school => {
              const schoolStats = getSchoolStats(groupedPDFs[school]);
              const isExpanded = expandedSchools.has(school);
              return (
                <div key={school} className="school-group">
                  <div 
                    className={`school-header ${isExpanded ? 'expanded' : ''}`}
                    onClick={() => toggleSchoolExpansion(school)}
                  >
                    <h3>{school} ({schoolStats.totalPDFs}件)</h3>
                    <div className="expand-icon">
                      {isExpanded ? '▼' : '▶'}
                    </div>
                  </div>
                  
                  {isExpanded && (
                    <div className="school-details">
                      <div className="school-stats">
                        <p><strong>科目:</strong> {schoolStats.subjects} ({schoolStats.subjectCount}種類)</p>
                        <p><strong>年度:</strong> {schoolStats.yearRange} ({schoolStats.yearCount}年)</p>
                      </div>
                      <div className="year-groups">
                        {Object.keys(groupedPDFs[school]).sort((a, b) => {
                          if (a === '不明') return 1;
                          if (b === '不明') return -1;
                          return parseInt(b) - parseInt(a); // 新しい年度順
                        }).map(year => {
                          const yearPDFs = groupedPDFs[school][year];
                          const yearKey = `${school}-${year}`;
                          const isYearExpanded = expandedYears.has(yearKey);
                          return (
                            <div key={year} className="year-group">
                              <div 
                                className={`year-header ${isYearExpanded ? 'expanded' : ''}`}
                                onClick={() => toggleYearExpansion(school, year)}
                              >
                                <h4>{year}年度 ({yearPDFs.length}件)</h4>
                                <div className="expand-icon">
                                  {isYearExpanded ? '▼' : '▶'}
                                </div>
                              </div>
                              
                              {isYearExpanded && (
                                <div className="year-details">
                                  <div className="pdf-grid">
                                    {yearPDFs.map(pdf => (
                                      <div key={pdf.id} className="pdf-card">
                                        <div className="pdf-info">
                                          <p><strong>科目:</strong> {getSubjectLabel(pdf.subject)}</p>
                                          <p>
                                            <strong>ファイル:</strong> 
                                            <button 
                                              className="pdf-filename-button"
                                              onClick={() => handlePDFClick(pdf.id)}
                                            >
                                              {pdf.filename}
                                            </button>
                                          </p>
                                        </div>
                                        <div className="pdf-actions">
                                          <button 
                                            className="view-button"
                                            onClick={() => handlePDFClick(pdf.id)}
                                          >
                                            過去問題表示
                                          </button>
                                          <button 
                                            className="ai-analysis-button"
                                            onClick={() => handleAIAnalysis(pdf)}
                                          >
                                            AI分析
                                          </button>
                                          {showAdminControls && (
                                            <button 
                                              className="question-manage-button"
                                              onClick={() => handleQuestionManage(pdf.id)}
                                            >
                                              問題管理
                                            </button>
                                          )}
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
      
      <AIAnalysisModal
        isOpen={aiAnalysisModalOpen}
        onClose={closeAIAnalysisModal}
        result={aiAnalysisResult}
        loading={aiAnalysisLoading}
        pdfName={selectedPdfForAnalysis?.filename || ''}
      />
    </>
  );
}; 