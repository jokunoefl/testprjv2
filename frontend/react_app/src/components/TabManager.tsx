import React, { useState } from 'react';
import { PDFUpload } from './PDFUpload';
import { PDFList } from './PDFList';
import { PDF } from '../types';

interface TabManagerProps {
  onPDFSelect: (pdfId: number) => void;
  onQuestionManage: (pdf: PDF) => void;
  onUploadSuccess: () => void;
  refreshKey: number;
}

export const TabManager: React.FC<TabManagerProps> = ({
  onPDFSelect,
  onQuestionManage,
  onUploadSuccess,
  refreshKey
}) => {
  const [activeTab, setActiveTab] = useState<'upload' | 'list'>('list');

  return (
    <div className="tab-manager">
      <div className="tab-header">
                       <button
                 className={`tab-button ${activeTab === 'list' ? 'active' : ''}`}
                 onClick={() => setActiveTab('list')}
               >
                 📚 過去問題一覧
               </button>
        <button
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          📤 PDFアップロード
        </button>
      </div>
      
      <div className="tab-content">
        {activeTab === 'list' && (
          <div className="tab-panel">
            <PDFList 
              key={refreshKey}
              onPDFSelect={onPDFSelect}
              onQuestionManage={onQuestionManage} 
            />
          </div>
        )}
        
        {activeTab === 'upload' && (
          <div className="tab-panel">
            <PDFUpload onUploadSuccess={onUploadSuccess} />
          </div>
        )}
      </div>
    </div>
  );
}; 