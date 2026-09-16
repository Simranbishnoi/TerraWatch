import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { signup } from '../api/client';
import logoImg from '../assets/terrawatch-logo.png';

export default function Signup() {
  const [fullName, setFullName] = useState('Jane Doe');
  const [email, setEmail] = useState('demo@terrawatch.com');
  const [password, setPassword] = useState('demo123');
  const [confirmPassword, setConfirmPassword] = useState('demo123');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const { loginUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      const data = await signup(email, password, fullName);
      if (loginUser && data?.token) {
        loginUser(data.token, data.email || email);
      }
      toast.success('Account created successfully');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err?.message || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F9F9F7] flex flex-col font-sans selection:bg-[#5A6B4A]/20">
      {/* Top Navbar */}
      <header className="w-full px-8 py-6 flex items-center justify-between">
        <div className="text-xl font-serif font-semibold tracking-tight text-[#1A1A1A]">
          TerraWatch
        </div>
        <nav className="hidden md:flex items-center space-x-8 text-sm text-gray-700">
          <a href="#benefits" className="hover:text-[#5A6B4A] transition-colors">
            Benefits
          </a>
          <a href="#specifications" className="hover:text-[#5A6B4A] transition-colors">
            Specifications
          </a>
          <a href="#howto" className="hover:text-[#5A6B4A] transition-colors">
            How-to
          </a>
          <a href="#contact" className="hover:text-[#5A6B4A] transition-colors">
            Contact Us
          </a>
        </nav>
        <div>
          <Link
            to="/login"
            className="inline-flex items-center justify-center bg-[#5A6B4A] text-white px-6 py-2 rounded-full text-sm font-medium hover:opacity-90 transition-opacity"
          >
            Log In
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-8">
        {/* Centered Large Logo */}
        <div className="flex flex-col items-center mb-6">
          <img
            src={logoImg}
            alt="TerraWatch Logo"
            className="w-48 h-48 sm:w-56 sm:h-56 md:w-64 md:h-64 object-contain mix-blend-multiply drop-shadow-sm transition-transform hover:scale-105 duration-300"
          />
        </div>

        {/* Scaled-down Headline */}
        <h1 className="font-serif text-3xl sm:text-4xl md:text-5xl font-medium text-[#1A1A1A] text-center mb-2 tracking-tight">
          Create account.
        </h1>

        {/* Subheadline */}
        <p className="text-gray-600 text-sm sm:text-base text-center max-w-md mb-8 font-normal leading-relaxed">
          The forensic lie detector for EUDR compliance.
        </p>

        {/* Signup Card */}
        <div className="bg-white rounded-[24px] shadow-xl p-8 sm:p-10 w-full max-w-md border border-gray-100">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Full Name Field */}
            <div>
              <label
                htmlFor="fullName"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Full Name
              </label>
              <input
                id="fullName"
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Jane Doe"
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition-all"
              />
            </div>

            {/* Email Field */}
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition-all"
              />
            </div>

            {/* Password Field */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 p-1 text-sm focus:outline-none"
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            {/* Confirm Password Field */}
            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Confirm Password
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 p-1 text-sm focus:outline-none"
                >
                  {showConfirmPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 bg-[#5A6B4A] text-white py-3.5 rounded-full font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed text-base"
            >
              {loading ? (
                <>
                  <svg
                    className="animate-spin h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  <span>Creating account...</span>
                </>
              ) : (
                <>
                  <span>Create Account</span>
                  <span className="text-lg leading-none font-bold">↗</span>
                </>
              )}
            </button>
          </form>

          {/* Bottom Link */}
          <div className="mt-8 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link
              to="/login"
              className="text-[#5A6B4A] font-semibold hover:underline"
            >
              Log in
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
