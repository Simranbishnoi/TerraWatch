import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ activePage = 'dashboard' }) {
  const { user, logoutUser } = useAuth();
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    if (logoutUser) logoutUser();
    toast.success('Logged out successfully');
    navigate('/login');
  };

  const userEmail = user?.email || 'demo@terrawatch.com';
  const avatarLetter = userEmail.charAt(0).toUpperCase();

  return (
    <header className="h-16 flex-shrink-0 bg-white border-b border-gray-200 px-6 sm:px-8 flex items-center justify-between z-30 shadow-xs">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <Link to="/dashboard" className="text-xl font-serif font-semibold tracking-tight text-[#1A1A1A] hover:opacity-90">
          TerraWatch
        </Link>
      </div>

      {/* Nav links */}
      <nav className="hidden md:flex items-center space-x-8 text-sm font-medium">
        <Link
          to="/dashboard"
          className={`py-5 px-1 transition-colors ${
            activePage === 'dashboard'
              ? 'text-[#5A6B4A] border-b-2 border-[#5A6B4A] font-semibold'
              : 'text-gray-600 hover:text-[#5A6B4A]'
          }`}
        >
          Dashboard
        </Link>
        <Link
          to="/farms"
          className={`py-5 px-1 transition-colors ${
            activePage === 'farms'
              ? 'text-[#5A6B4A] border-b-2 border-[#5A6B4A] font-semibold'
              : 'text-gray-600 hover:text-[#5A6B4A]'
          }`}
        >
          Farms
        </Link>
        <Link
          to="/reports"
          className={`py-5 px-1 transition-colors ${
            activePage === 'reports'
              ? 'text-[#5A6B4A] border-b-2 border-[#5A6B4A] font-semibold'
              : 'text-gray-600 hover:text-[#5A6B4A]'
          }`}
        >
          Reports
        </Link>
        <Link
          to="/ocean"
          className={`py-5 px-1 transition-colors ${
            activePage === 'ocean'
              ? 'text-[#5A6B4A] border-b-2 border-[#5A6B4A] font-semibold'
              : 'text-gray-600 hover:text-[#5A6B4A]'
          }`}
        >
          Ocean
        </Link>
      </nav>

      {/* Right: User Avatar Dropdown */}
      <div className="relative">
        <button
          onClick={() => setUserMenuOpen(!userMenuOpen)}
          aria-label="Open user profile menu"
          className="w-9 h-9 rounded-full bg-[#5A6B4A] text-white flex items-center justify-center text-sm font-medium shadow-sm hover:opacity-95 ring-2 ring-offset-2 ring-[#5A6B4A]/30 transition active:scale-95"
        >
          {avatarLetter}
        </button>

        {userMenuOpen && (
          <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-xl border border-gray-100 py-2 z-50 animate-fade-in">
            <div className="px-4 py-2 border-b border-gray-100">
              <p className="text-xs text-gray-400 font-medium">Signed in as</p>
              <p className="text-sm font-semibold text-gray-900 truncate">{userEmail}</p>
            </div>
            <button
              onClick={handleLogout}
              className="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 font-medium transition flex items-center gap-2"
            >
              <span>Logout</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
