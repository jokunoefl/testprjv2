import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useParams } from 'react-router-dom';
import './App.css';

import { AdminTabManager } from './components/AdminTabManager';
import { UserTabManager } from './components/UserTabManager';
import { PDFViewer } from './components/PDFViewer';
import { QuestionManager } from './components/QuestionManager';
import { Login } from './components/Login';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { PDF } from './types';

function PDFViewerWrapper() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  console.log('PDFViewerWrapper: PDF ID =', id);
  
  if (!id) return <div>PDF ID not found</div>;
  
  return (
    <PDFViewer 
      pdfId={parseInt(id)} 
      onBack={() => navigate('/')} 
    />
  );
}

function AppContent() {
  const { user, isAuthenticated, isAdmin, isGuest, logout, loading } = useAuth();
  const [managingQuestions, setManagingQuestions] = useState<PDF | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const navigate = useNavigate();

  const handlePDFSelect = (pdfId: number) => {
    console.log('PDF表示画面に遷移します:', pdfId);
    navigate(`/pdf/${pdfId}`);
  };

  const handleQuestionManage = (pdf: PDF) => {
    setManagingQuestions(pdf);
  };

  const handleCloseQuestionManager = () => {
    setManagingQuestions(null);
  };

  const handleUploadSuccess = () => {
    setRefreshKey(prev => prev + 1);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (loading) {
    return <div className="loading">読み込み中...</div>;
  }

  if (!isAuthenticated && !isGuest) {
    return <Login />;
  }

  if (managingQuestions) {
    return (
      <QuestionManager 
        pdf={managingQuestions} 
        onClose={handleCloseQuestionManager} 
      />
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>中学受験過去問題管理システム</h1>
          <div className="user-info">
            <span className="username">
              {user?.username} ({user?.role === 'admin' ? '管理者' : user?.role === 'guest' ? 'ゲスト' : '一般ユーザー'})
              {user?.role === 'guest' && ' (AI分析利用可能)'}
            </span>
            <button onClick={handleLogout} className="logout-button">
              {isGuest ? '終了' : 'ログアウト'}
            </button>
          </div>
        </div>
      </header>
      
      <main className="App-main">
        <Routes>
          <Route path="/" element={
            isAdmin ? (
              <AdminTabManager
                onPDFSelect={handlePDFSelect}
                onQuestionManage={handleQuestionManage}
                onUploadSuccess={handleUploadSuccess}
                refreshKey={refreshKey}
              />
            ) : (
              <UserTabManager
                onPDFSelect={handlePDFSelect}
                refreshKey={refreshKey}
              />
            )
          } />
          <Route path="/pdf/:id" element={<PDFViewerWrapper />} />
          <Route path="*" element={
            <div style={{ padding: '20px', textAlign: 'center' }}>
              <h2>ページが見つかりません</h2>
              <p>お探しのページは存在しないか、移動された可能性があります。</p>
              <button onClick={() => navigate('/')} style={{ padding: '10px 20px', marginTop: '10px' }}>
                ホームに戻る
              </button>
            </div>
          } />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;
