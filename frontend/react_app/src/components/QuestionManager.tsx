import React, { useState, useEffect } from 'react';
import { PDF, Question, QuestionType, PDFWithQuestions } from '../types';
import { pdfApi, questionTypeApi, questionApi } from '../services/api';
import { BatchQuestionInput } from './BatchQuestionInput';

interface QuestionManagerProps {
  pdf: PDF;
  onClose: () => void;
}

export const QuestionManager: React.FC<QuestionManagerProps> = ({ pdf, onClose }) => {
  const [pdfWithQuestions, setPdfWithQuestions] = useState<PDFWithQuestions | null>(null);
  const [questionTypes, setQuestionTypes] = useState<QuestionType[]>([]);
  const [isManualAdding, setIsManualAdding] = useState(false);
  const [isBatchAdding, setIsBatchAdding] = useState(false);
  const [isEditingPDF, setIsEditingPDF] = useState(false);
  const [pdfEditData, setPdfEditData] = useState({
    school: pdf.school,
    subject: pdf.subject,
    year: pdf.year
  });
  const [newQuestion, setNewQuestion] = useState({
    question_number: '',
    question_text: '',
    answer_text: '',
    difficulty_level: 1,
    points: 0,
    page_number: 1,
    question_type_id: 1,
    keywords: ''
  });

  useEffect(() => {
    loadData();
  }, [pdf.id]);

  const loadData = async () => {
    try {
      const [pdfData, typesData] = await Promise.all([
        pdfApi.getPDFWithQuestions(pdf.id),
        questionTypeApi.getQuestionTypes()
      ]);
      setPdfWithQuestions(pdfData);
      setQuestionTypes(typesData);
    } catch (error) {
      console.error('データ読み込みエラー:', error);
    }
  };

  const handleManualAdd = async () => {
    try {
      await questionApi.createQuestion({
        pdf_id: pdf.id,
        ...newQuestion
      });
      setNewQuestion({
        question_number: '',
        question_text: '',
        answer_text: '',
        difficulty_level: 1,
        points: 0,
        page_number: 1,
        question_type_id: 1,
        keywords: ''
      });
      setIsManualAdding(false);
      await loadData();
      alert('問題を追加しました');
    } catch (error) {
      alert('問題の追加に失敗しました');
    }
  };

  const handleDeleteQuestion = async (questionId: number) => {
    if (window.confirm('この問題を削除しますか？')) {
      try {
        await questionApi.deleteQuestion(questionId);
        await loadData();
        alert('問題を削除しました');
      } catch (error) {
        alert('問題の削除に失敗しました');
      }
    }
  };

  const getQuestionTypeName = (questionTypeId: number) => {
    const questionType = questionTypes.find(type => type.id === questionTypeId);
    return questionType?.name || '不明';
  };

  const handlePDFEdit = async () => {
    try {
      await pdfApi.updatePDF(pdf.id, pdfEditData);
      await loadData();
      setIsEditingPDF(false);
      alert('PDF情報を更新しました');
    } catch (error) {
      console.error('PDF更新エラー:', error);
      alert('PDF情報の更新に失敗しました');
    }
  };

  const handlePDFEditCancel = () => {
    setPdfEditData({
      school: pdf.school,
      subject: pdf.subject,
      year: pdf.year
    });
    setIsEditingPDF(false);
  };

  return (
    <div className="question-manager">
      <div className="question-manager-header">
        <h2>問題管理 - {pdf.filename}</h2>
        <button onClick={onClose} className="close-btn">×</button>
      </div>

      <div className="question-manager-content">
        <div className="pdf-info">
          {isEditingPDF ? (
            <div className="pdf-edit-form">
              <h3>PDF情報編集</h3>
              <div className="form-group">
                <label>学校名:</label>
                <input
                  type="text"
                  value={pdfEditData.school}
                  onChange={(e) => setPdfEditData({...pdfEditData, school: e.target.value})}
                  placeholder="学校名を入力"
                />
              </div>
              <div className="form-group">
                <label>科目:</label>
                <select
                  value={pdfEditData.subject}
                  onChange={(e) => setPdfEditData({...pdfEditData, subject: e.target.value})}
                >
                  <option value="math">算数</option>
                  <option value="japanese">国語</option>
                  <option value="science">理科</option>
                  <option value="social">社会</option>
                  <option value="unknown">不明</option>
                </select>
              </div>
              <div className="form-group">
                <label>年度:</label>
                <input
                  type="number"
                  value={pdfEditData.year}
                  onChange={(e) => setPdfEditData({...pdfEditData, year: parseInt(e.target.value)})}
                  placeholder="年度を入力"
                  min="2000"
                  max="2030"
                />
              </div>
              <div className="form-actions">
                <button onClick={handlePDFEdit} className="save-btn">保存</button>
                <button onClick={handlePDFEditCancel} className="cancel-btn">キャンセル</button>
              </div>
            </div>
          ) : (
            <>
              <p><strong>学校:</strong> {pdf.school}</p>
              <p><strong>科目:</strong> {pdf.subject}</p>
              <p><strong>年度:</strong> {pdf.year}</p>
              <button 
                onClick={() => setIsEditingPDF(true)}
                className="edit-pdf-btn"
              >
                編集
              </button>
            </>
          )}
        </div>

        <div className="action-buttons">
          <button 
            onClick={() => setIsManualAdding(true)}
            className="manual-add-btn"
          >
            手動で問題を追加
          </button>

          <button 
            onClick={() => setIsBatchAdding(true)}
            className="batch-add-btn"
          >
            複数問題一括入力
          </button>
        </div>

        {isManualAdding && (
          <div className="manual-add-form">
            <h3>手動問題入力</h3>
            <div className="form-group">
              <label>問題番号:</label>
              <input
                type="text"
                value={newQuestion.question_number}
                onChange={(e) => setNewQuestion({...newQuestion, question_number: e.target.value})}
                placeholder="例: 1, 2, 1-1"
              />
            </div>
            <div className="form-group">
              <label>問題文:</label>
              <textarea
                value={newQuestion.question_text}
                onChange={(e) => setNewQuestion({...newQuestion, question_text: e.target.value})}
                placeholder="問題文を入力してください"
                rows={4}
              />
            </div>
            <div className="form-group">
              <label>解答:</label>
              <textarea
                value={newQuestion.answer_text}
                onChange={(e) => setNewQuestion({...newQuestion, answer_text: e.target.value})}
                placeholder="解答を入力してください（オプション）"
                rows={2}
              />
            </div>
            <div className="form-group">
              <label>キーワード:</label>
              <input
                type="text"
                value={newQuestion.keywords}
                onChange={(e) => setNewQuestion({...newQuestion, keywords: e.target.value})}
                placeholder="例: 関数, グラフ, 計算（カンマ区切り）"
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>問題タイプ:</label>
                <select
                  value={newQuestion.question_type_id}
                  onChange={(e) => setNewQuestion({...newQuestion, question_type_id: parseInt(e.target.value)})}
                >
                  {questionTypes.map(type => (
                    <option key={type.id} value={type.id}>{type.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>難易度:</label>
                <select
                  value={newQuestion.difficulty_level}
                  onChange={(e) => setNewQuestion({...newQuestion, difficulty_level: parseInt(e.target.value)})}
                >
                  <option value={1}>易しい</option>
                  <option value={2}>普通</option>
                  <option value={3}>難しい</option>
                </select>
              </div>
              <div className="form-group">
                <label>配点:</label>
                <input
                  type="number"
                  value={newQuestion.points}
                  onChange={(e) => setNewQuestion({...newQuestion, points: parseInt(e.target.value) || 0})}
                  min="0"
                />
              </div>
              <div className="form-group">
                <label>ページ:</label>
                <input
                  type="number"
                  value={newQuestion.page_number}
                  onChange={(e) => setNewQuestion({...newQuestion, page_number: parseInt(e.target.value) || 1})}
                  min="1"
                />
              </div>
            </div>
            <div className="form-actions">
              <button onClick={handleManualAdd} className="save-btn">保存</button>
              <button onClick={() => setIsManualAdding(false)} className="cancel-btn">キャンセル</button>
            </div>
          </div>
        )}

        <div className="questions-list">
          <h3>登録済み問題 ({pdfWithQuestions?.questions.length || 0}件)</h3>
          {pdfWithQuestions?.questions.length === 0 ? (
            <p className="no-questions">まだ問題が登録されていません</p>
          ) : (
            <div className="questions-grid">
              {pdfWithQuestions?.questions.map((question) => (
                <div key={question.id} className="question-card">
                  <div className="question-header">
                    <span className="question-number">問題 {question.question_number}</span>
                    <span className="question-type">
                      {getQuestionTypeName(question.question_type_id)}
                    </span>
                    <span className="question-points">{question.points}点</span>
                  </div>
                  <div className="question-content">
                    <p className="question-text">{question.question_text}</p>
                    {question.answer_text && (
                      <p className="answer-text"><strong>解答:</strong> {question.answer_text}</p>
                    )}
                    {question.keywords && (
                      <p className="keywords"><strong>キーワード:</strong> {question.keywords}</p>
                    )}
                  </div>
                  <div className="question-footer">
                    <span className="difficulty">難易度: {question.difficulty_level}</span>
                    <span className="page">ページ: {question.page_number}</span>
                    <div className="question-actions">
                      <button className="edit-btn">編集</button>
                      <button 
                        onClick={() => handleDeleteQuestion(question.id)}
                        className="delete-btn"
                      >
                        削除
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* バッチ入力モーダル */}
      {isBatchAdding && (
        <BatchQuestionInput
          pdfId={pdf.id}
          questionTypes={questionTypes}
          onQuestionsAdded={loadData}
          onClose={() => setIsBatchAdding(false)}
        />
      )}
    </div>
  );
}; 