import React from 'react';
import { PDFList } from './PDFList';

interface UserTabManagerProps {
  onPDFSelect: (pdfId: number) => void;
  refreshKey: number;
}

export const UserTabManager: React.FC<UserTabManagerProps> = ({
  onPDFSelect,
  refreshKey
}) => {
  return (
    <div className="tab-manager">
      <div className="tab-header">
        <button className="tab-button active">
          📚 過去問題一覧・AI分析
        </button>
      </div>
      
      <div className="tab-content">
        <div className="tab-panel">
          <PDFList 
            key={refreshKey}
            onPDFSelect={onPDFSelect}
            showAdminControls={false}
          />
        </div>
      </div>
    </div>
  );
}; 