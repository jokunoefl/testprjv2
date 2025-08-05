import React, { useState } from 'react';
import { QuestionType } from '../types';

interface BatchQuestionInputProps {
  pdfId: number;
  questionTypes: QuestionType[];
  onQuestionsAdded: () => void;
  onClose: () => void;
}

interface BatchQuestion {
  question_number: string;
  question_text: string;
  answer_text: string;
  difficulty_level: number;
  points: number;
  page_number: number;
  question_type_id: number;
  keywords: string;
}

export const BatchQuestionInput: React.FC<BatchQuestionInputProps> = ({
  pdfId,
  questionTypes,
  onQuestionsAdded,
  onClose
}) => {
  const [questions, setQuestions] = useState<BatchQuestion[]>([
    {
      question_number: '',
      question_text: '',
      answer_text: '',
      difficulty_level: 1,
      points: 0,
      page_number: 1,
      question_type_id: 1,
      keywords: ''
    }
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const addQuestion = () => {
    setQuestions([...questions, {
      question_number: '',
      question_text: '',
      answer_text: '',
      difficulty_level: 1,
      points: 0,
      page_number: 1,
      question_type_id: 1,
      keywords: ''
    }]);
  };

  const removeQuestion = (index: number) => {
    if (questions.length > 1) {
      setQuestions(questions.filter((_, i) => i !== index));
    }
  };

  const updateQuestion = (index: number, field: keyof BatchQuestion, value: any) => {
    const updatedQuestions = [...questions];
    updatedQuestions[index] = { ...updatedQuestions[index], [field]: value };
    setQuestions(updatedQuestions);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      // 空でない問題のみをフィルタリング
      const validQuestions = questions.filter(q => 
        q.question_number.trim() && q.question_text.trim()
      );

      if (validQuestions.length === 0) {
        alert('少なくとも1つの問題を入力してください');
        return;
      }

      // 各問題を順次保存
      for (const question of validQuestions) {
        await fetch(`http://localhost:8001/questions/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            pdf_id: pdfId,
            ...question
          }),
        });
      }

      alert(`${validQuestions.length}個の問題を追加しました`);
      onQuestionsAdded();
      onClose();
    } catch (error) {
      alert('問題の追加に失敗しました');
      console.error('Error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePasteFromExcel = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const pastedText = e.target.value;
    const lines = pastedText.split('\n').filter(line => line.trim());
    
    const parsedQuestions: BatchQuestion[] = lines.map((line, index) => {
      const columns = line.split('\t');
      return {
        question_number: columns[0] || `${index + 1}`,
        question_text: columns[1] || '',
        answer_text: columns[2] || '',
        difficulty_level: parseInt(columns[3]) || 1,
        points: parseInt(columns[4]) || 0,
        page_number: parseInt(columns[5]) || 1,
        question_type_id: parseInt(columns[6]) || 1,
        keywords: columns[7] || ''
      };
    });

    setQuestions(parsedQuestions);
  };

  return (
    <div className="batch-input-modal">
      <div className="batch-input-content">
        <div className="batch-input-header">
          <h2>複数問題一括入力</h2>
          <button onClick={onClose} className="close-btn">×</button>
        </div>

        <div className="batch-input-body">
          <div className="paste-section">
            <h3>Excelからの貼り付け</h3>
            <p>Excelからコピーしたデータを貼り付けてください（タブ区切り）</p>
            <p className="format-hint">
              形式: 問題番号 [Tab] 問題文 [Tab] 解答 [Tab] 難易度 [Tab] 配点 [Tab] ページ [Tab] 問題タイプID [Tab] キーワード
            </p>
            <textarea
              placeholder="Excelからコピーしたデータをここに貼り付けてください..."
              onChange={handlePasteFromExcel}
              rows={5}
              className="paste-textarea"
            />
          </div>

          <div className="manual-batch-section">
            <div className="section-header">
              <h3>手動入力</h3>
              <button onClick={addQuestion} className="add-question-btn">
                + 問題を追加
              </button>
            </div>

            {questions.map((question, index) => (
              <div key={index} className="question-input-group">
                <div className="question-header">
                  <h4>問題 {index + 1}</h4>
                  {questions.length > 1 && (
                    <button 
                      onClick={() => removeQuestion(index)}
                      className="remove-question-btn"
                    >
                      ×
                    </button>
                  )}
                </div>

                <div className="question-fields">
                  <div className="field-row">
                    <div className="field-group">
                      <label>問題番号:</label>
                      <input
                        type="text"
                        value={question.question_number}
                        onChange={(e) => updateQuestion(index, 'question_number', e.target.value)}
                        placeholder="例: 1, 2, 1-1"
                      />
                    </div>
                    <div className="field-group">
                      <label>問題タイプ:</label>
                      <select
                        value={question.question_type_id}
                        onChange={(e) => updateQuestion(index, 'question_type_id', parseInt(e.target.value))}
                      >
                        {questionTypes.map(type => (
                          <option key={type.id} value={type.id}>{type.name}</option>
                        ))}
                      </select>
                    </div>
                    <div className="field-group">
                      <label>難易度:</label>
                      <select
                        value={question.difficulty_level}
                        onChange={(e) => updateQuestion(index, 'difficulty_level', parseInt(e.target.value))}
                      >
                        <option value={1}>易しい</option>
                        <option value={2}>普通</option>
                        <option value={3}>難しい</option>
                      </select>
                    </div>
                    <div className="field-group">
                      <label>配点:</label>
                      <input
                        type="number"
                        value={question.points}
                        onChange={(e) => updateQuestion(index, 'points', parseInt(e.target.value) || 0)}
                        min="0"
                      />
                    </div>
                    <div className="field-group">
                      <label>ページ:</label>
                      <input
                        type="number"
                        value={question.page_number}
                        onChange={(e) => updateQuestion(index, 'page_number', parseInt(e.target.value) || 1)}
                        min="1"
                      />
                    </div>
                    <div className="field-group">
                      <label>キーワード:</label>
                      <input
                        type="text"
                        value={question.keywords}
                        onChange={(e) => updateQuestion(index, 'keywords', e.target.value)}
                        placeholder="キーワードを入力してください（オプション）"
                      />
                    </div>
                  </div>

                  <div className="field-group">
                    <label>問題文:</label>
                    <textarea
                      value={question.question_text}
                      onChange={(e) => updateQuestion(index, 'question_text', e.target.value)}
                      placeholder="問題文を入力してください"
                      rows={3}
                    />
                  </div>

                  <div className="field-group">
                    <label>解答:</label>
                    <textarea
                      value={question.answer_text}
                      onChange={(e) => updateQuestion(index, 'answer_text', e.target.value)}
                      placeholder="解答を入力してください（オプション）"
                      rows={2}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="batch-input-actions">
          <button 
            onClick={handleSubmit} 
            disabled={isSubmitting}
            className="submit-btn"
          >
            {isSubmitting ? '保存中...' : `${questions.length}個の問題を保存`}
          </button>
          <button onClick={onClose} className="cancel-btn">
            キャンセル
          </button>
        </div>
      </div>
    </div>
  );
}; 