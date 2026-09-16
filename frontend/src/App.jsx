import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import Dashboard from './pages/Dashboard';
import Farms from './pages/Farms';
import Reports from './pages/Reports';
import Ocean from './pages/Ocean';
import Business from './pages/Business';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Footer from './components/Footer';

// Protected Route Wrapper
function Protected({ children }) {
  const { user } = useAuth();
  if (!user || !user.token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="bottom-right" />
        <div className="min-h-screen flex flex-col bg-[#F9F9F7] text-[#1A1A1A]">
          <div className="flex-1 flex flex-col">
            <Routes>
              {/* 1. Root path redirects to /login */}
              <Route path="/" element={<Navigate to="/login" replace />} />

              {/* 2. Public auth routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />

              {/* 3. Protected application routes */}
              <Route
                path="/dashboard"
                element={
                  <Protected>
                    <Dashboard />
                  </Protected>
                }
              />
              <Route
                path="/farms"
                element={
                  <Protected>
                    <Farms />
                  </Protected>
                }
              />
              <Route
                path="/reports"
                element={
                  <Protected>
                    <Reports />
                  </Protected>
                }
              />
              <Route
                path="/ocean"
                element={
                  <Protected>
                    <Ocean />
                  </Protected>
                }
              />
              <Route
                path="/business"
                element={
                  <Protected>
                    <Business />
                  </Protected>
                }
              />

              {/* Catch-all route */}
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </div>
          <Footer />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

