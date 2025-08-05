import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface User {
  id: number;
  username: string;
  role: 'admin' | 'user' | 'guest';
  email?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isGuest: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  loginAsGuest: () => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // 初期化時にローカルストレージからユーザー情報を復元
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Failed to parse saved user:', error);
        localStorage.removeItem('user');
        // エラーが発生した場合はゲストとして自動ログイン
        const guestUser: User = {
          id: 0,
          username: 'guest',
          role: 'guest',
          email: undefined
        };
        setUser(guestUser);
        localStorage.setItem('user', JSON.stringify(guestUser));
      }
    } else {
      // 保存されたユーザー情報がない場合はゲストとして自動ログイン
      const guestUser: User = {
        id: 0,
        username: 'guest',
        role: 'guest',
        email: undefined
      };
      setUser(guestUser);
      localStorage.setItem('user', JSON.stringify(guestUser));
    }
    setLoading(false);
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    // 簡易的な認証（実際のプロジェクトではバックエンドAPIを使用）
    if (username === 'admin' && password === 'admin123') {
      const adminUser: User = {
        id: 1,
        username: 'admin',
        role: 'admin',
        email: 'admin@example.com'
      };
      setUser(adminUser);
      localStorage.setItem('user', JSON.stringify(adminUser));
      return true;
    } else if (username === 'user' && password === 'user123') {
      const regularUser: User = {
        id: 2,
        username: 'user',
        role: 'user',
        email: 'user@example.com'
      };
      setUser(regularUser);
      localStorage.setItem('user', JSON.stringify(regularUser));
      return true;
    }
    return false;
  };

  const loginAsGuest = () => {
    const guestUser: User = {
      id: 0,
      username: 'guest',
      role: 'guest',
      email: undefined
    };
    setUser(guestUser);
    localStorage.setItem('user', JSON.stringify(guestUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    isGuest: user?.role === 'guest',
    login,
    loginAsGuest,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 