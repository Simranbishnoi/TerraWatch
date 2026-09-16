import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-6xl mx-auto py-12 px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
          {/* Left Column: Brand & Tagline */}
          <div className="flex flex-col space-y-3">
            <Link
              to="/dashboard"
              className="text-2xl font-serif font-semibold tracking-tight text-[#1A1A1A] hover:opacity-90 transition-opacity"
            >
              TerraWatch
            </Link>
            <p className="text-sm text-gray-600 leading-relaxed font-sans max-w-sm">
              The forensic lie detector for EUDR compliance
            </p>
          </div>

          {/* Center Column: Quick Navigation Links */}
          <div className="flex flex-col space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400 font-sans">
              Navigation
            </h3>
            <div className="flex flex-col space-y-2 text-sm font-medium">
              <Link
                to="/dashboard"
                className="text-gray-600 hover:text-[#5A6B4A] transition-colors"
              >
                Dashboard
              </Link>
              <Link
                to="/farms"
                className="text-gray-600 hover:text-[#5A6B4A] transition-colors"
              >
                Farms
              </Link>
              <Link
                to="/reports"
                className="text-gray-600 hover:text-[#5A6B4A] transition-colors"
              >
                Reports
              </Link>
              <Link
                to="/business"
                className="text-gray-600 hover:text-[#5A6B4A] transition-colors"
              >
                Business
              </Link>
              <Link
                to="/ocean"
                className="text-gray-600 hover:text-[#5A6B4A] transition-colors"
              >
                Ocean
              </Link>
            </div>
          </div>

          {/* Right Column: Contact & Socials */}
          <div className="flex flex-col space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400 font-sans">
              Contact Us
            </h3>
            <div className="flex flex-col space-y-2 text-sm">
              <a
                href="mailto:hello@terrawatch.com"
                className="text-gray-600 hover:text-[#5A6B4A] transition-colors font-medium"
              >
                hello@terrawatch.com
              </a>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-[#5A6B4A] transition-colors font-medium inline-flex items-center gap-1"
              >
                GitHub <span>↗</span>
              </a>
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-[#5A6B4A] transition-colors font-medium inline-flex items-center gap-1"
              >
                LinkedIn <span>↗</span>
              </a>
            </div>
          </div>
        </div>

        {/* Bottom Bar: Copyright */}
        <div className="mt-12 pt-8 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-400">
          <p>© 2026 TerraWatch. All rights reserved.</p>
          <p className="mt-2 sm:mt-0 font-sans text-stone-400">
            Satellite Verification & Forensic Monitoring
          </p>
        </div>
      </div>
    </footer>
  );
}
