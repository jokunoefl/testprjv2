import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Login.css';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, loginAsGuest } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const success = await login(username, password);
      if (!success) {
        setError('ユーザー名またはパスワードが正しくありません。');
      }
    } catch (err) {
      setError('ログイン中にエラーが発生しました。');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>中学受験過去問題管理システム</h1>
          <p>ログインしてください</p>
        </div>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">ユーザー名</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">パスワード</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <button type="submit" disabled={loading} className="login-button">
            {loading ? 'ログイン中...' : 'ログイン'}
          </button>
        </form>
        
        <div className="guest-access">
          <div className="divider">
            <span>または</span>
          </div>
          <button 
            onClick={loginAsGuest} 
            className="guest-button"
            disabled={loading}
          >
            👤 ゲストとして閲覧
          </button>
        </div>
        
        <div className="login-info">
          <h3>テスト用アカウント</h3>
          <div className="account-info">
            <div>
              <strong>管理者:</strong> admin / admin123
            </div>
            <div>
              <strong>一般ユーザー:</strong> user / user123
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 