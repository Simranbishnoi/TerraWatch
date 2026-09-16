import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('tw_user');
    return saved ? JSON.parse(saved) : { email: 'demo@terrawatch.com', token: 'mock-token' };
  });

  const loginUser = (token, email) => {
    const userData = { email, token };
    setUser(userData);
    localStorage.setItem('tw_user', JSON.stringify(userData));
  };

  const logoutUser = () => {
    setUser(null);
    localStorage.removeItem('tw_user');
  };

  return (
    <AuthContext.Provider value={{ user, loginUser, logoutUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    return {
      user: { email: 'demo@terrawatch.com', token: 'mock-token' },
      loginUser: () => {},
      logoutUser: () => {},
    };
  }
  return ctx;
}
