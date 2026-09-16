import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';

export default function Business() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#F9F9F7] text-[#1A1A1A] font-sans selection:bg-[#5A6B4A]/20 flex flex-col">
      {/* Navbar */}
      <Navbar activePage="business" />

      {/* Main Content */}
      <main className="max-w-5xl w-full mx-auto px-6 sm:px-8 py-14 flex-1">
        {/* SECTION 1 — HERO */}
        <section className="mb-14">
          <p className="text-xs tracking-widest text-[#5A6B4A] font-semibold uppercase mb-4">
            THE BUSINESS CASE
          </p>
          <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl text-gray-900 font-medium tracking-tight leading-tight">
            What we do. How we do it. How we profit.
          </h1>
          <p className="text-gray-500 text-lg sm:text-xl mt-4 max-w-2xl font-light leading-relaxed">
            TerraWatch is the forensic lie detector for EUDR compliance.
          </p>
        </section>

        {/* SECTION 2 — WHAT WE DO */}
        <section className="bg-white rounded-3xl p-8 sm:p-10 border border-gray-100 shadow-xs mb-8">
          <h2 className="font-serif text-2xl sm:text-3xl text-gray-900 mb-4 font-medium tracking-tight">
            What We Do
          </h2>
          <p className="text-gray-600 text-base sm:text-lg leading-relaxed mb-8">
            We use free satellite imagery (Sentinel-2) and AI change detection to verify whether companies are lying about deforestation in their supply chains. Regulators and audit firms use us to catch fraud before it becomes a fine.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 border-t border-gray-100">
            <div className="bg-[#F9F9F7] rounded-2xl p-5 border border-gray-100/80">
              <span className="block font-serif text-2xl font-semibold text-gray-900">
                10M ha
              </span>
              <span className="text-xs text-gray-500 font-medium">
                Lost per year globally
              </span>
            </div>
            <div className="bg-[#F9F9F7] rounded-2xl p-5 border border-gray-100/80">
              <span className="block font-serif text-2xl font-semibold text-red-700">
                $2 Billion
              </span>
              <span className="text-xs text-gray-500 font-medium">
                Fraudulent carbon credits
              </span>
            </div>
            <div className="bg-[#F9F9F7] rounded-2xl p-5 border border-gray-100/80">
              <span className="block font-serif text-2xl font-semibold text-[#5A6B4A]">
                4% Turnover
              </span>
              <span className="text-xs text-gray-500 font-medium">
                Maximum EU fine penalty
              </span>
            </div>
          </div>
        </section>

        {/* SECTION 3 — HOW WE DO IT */}
        <section className="bg-white rounded-3xl p-8 sm:p-10 border border-gray-100 shadow-xs mb-8">
          <h2 className="font-serif text-2xl sm:text-3xl text-gray-900 mb-6 font-medium tracking-tight">
            How We Do It
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Step 1 */}
            <div className="relative flex flex-col justify-between p-5 bg-[#F9F9F7] rounded-2xl border border-gray-100">
              <div>
                <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#5A6B4A]/10 text-[#5A6B4A] font-mono text-sm font-semibold mb-3">
                  01
                </span>
                <h3 className="text-base font-semibold text-gray-900 mb-1.5">
                  Upload
                </h3>
                <p className="text-xs text-gray-500 leading-relaxed">
                  Company submits farm polygon coordinates or cadastral boundaries.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="relative flex flex-col justify-between p-5 bg-[#F9F9F7] rounded-2xl border border-gray-100">
              <div>
                <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#5A6B4A]/10 text-[#5A6B4A] font-mono text-sm font-semibold mb-3">
                  02
                </span>
                <h3 className="text-base font-semibold text-gray-900 mb-1.5">
                  Analyze
                </h3>
                <p className="text-xs text-gray-500 leading-relaxed">
                  We pull 4 years of Sentinel-2 imagery and compute NDVI & SAR change vectors.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="relative flex flex-col justify-between p-5 bg-[#F9F9F7] rounded-2xl border border-gray-100">
              <div>
                <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#5A6B4A]/10 text-[#5A6B4A] font-mono text-sm font-semibold mb-3">
                  03
                </span>
                <h3 className="text-base font-semibold text-gray-900 mb-1.5">
                  Detect
                </h3>
                <p className="text-xs text-gray-500 leading-relaxed">
                  AI flags historical canopy loss, buffer degradation, and boundary manipulation.
                </p>
              </div>
            </div>

            {/* Step 4 */}
            <div className="relative flex flex-col justify-between p-5 bg-[#F9F9F7] rounded-2xl border border-gray-100">
              <div>
                <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#5A6B4A]/10 text-[#5A6B4A] font-mono text-sm font-semibold mb-3">
                  04
                </span>
                <h3 className="text-base font-semibold text-gray-900 mb-1.5">
                  Report
                </h3>
                <p className="text-xs text-gray-500 leading-relaxed">
                  Generate audit-ready, cryptographically stamped PDF with satellite proof.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 4 — HOW WE PROFIT */}
        <section className="bg-white rounded-3xl p-8 sm:p-10 border border-gray-100 shadow-xs mb-8">
          <h2 className="font-serif text-2xl sm:text-3xl text-gray-900 mb-8 font-medium tracking-tight">
            How We Profit
          </h2>

          {/* Unit Economics Box */}
          <div className="bg-[#F9F9F7] rounded-2xl p-6 sm:p-8 mb-8 border border-gray-200/70">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 divide-y md:divide-y-0 md:divide-x divide-gray-200">
              {/* Cost side */}
              <div className="md:pr-6">
                <span className="text-xs font-semibold uppercase tracking-wider text-gray-400 block mb-2 font-mono">
                  Our Cost Per Analysis
                </span>
                <div className="font-serif text-5xl sm:text-6xl text-gray-900 font-medium tracking-tight mb-3">
                  $0.0015
                </div>
                <p className="text-xs text-gray-500 font-mono">
                  Sentinel-2: Free • Compute: $0.001 • Hosting: $0.0005
                </p>
              </div>

              {/* Price side */}
              <div className="pt-6 md:pt-0 md:pl-8">
                <span className="text-xs font-semibold uppercase tracking-wider text-[#5A6B4A] block mb-2 font-mono">
                  Our Price
                </span>
                <div className="font-serif text-5xl sm:text-6xl text-[#5A6B4A] font-medium tracking-tight mb-3">
                  $0.05
                </div>
                <p className="text-sm font-semibold text-[#5A6B4A] flex items-center gap-2">
                  <span className="bg-[#5A6B4A]/10 px-2.5 py-0.5 rounded-full">
                    Gross Margin: 97%
                  </span>
                </p>
              </div>
            </div>
          </div>

          {/* Customer Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Card 1 */}
            <div className="p-6 rounded-2xl bg-[#F9F9F7] border border-gray-100 flex flex-col justify-between">
              <div>
                <span className="text-xs font-mono text-[#5A6B4A] font-semibold uppercase block mb-1">
                  Enforcement Tier
                </span>
                <h3 className="font-serif text-lg text-gray-900 font-medium mb-2">
                  EU Enforcement Agencies
                </h3>
                <p className="text-xs text-gray-600 leading-relaxed mb-4">
                  $500K/year per agency. One caught fraud case = millions in avoided fines.
                </p>
              </div>
              <span className="text-xs font-semibold text-gray-900 bg-white border border-gray-200 px-3 py-1.5 rounded-lg inline-block text-center shadow-2xs">
                $500,000 / year
              </span>
            </div>

            {/* Card 2 */}
            <div className="p-6 rounded-2xl bg-[#F9F9F7] border border-gray-100 flex flex-col justify-between">
              <div>
                <span className="text-xs font-mono text-[#5A6B4A] font-semibold uppercase block mb-1">
                  Assurance Tier
                </span>
                <h3 className="font-serif text-lg text-gray-900 font-medium mb-2">
                  Big Four Audit Firms
                </h3>
                <p className="text-xs text-gray-600 leading-relaxed mb-4">
                  $50K/year + $0.05/farm. Pre-audit screening for enterprise ESG assurance.
                </p>
              </div>
              <span className="text-xs font-semibold text-gray-900 bg-white border border-gray-200 px-3 py-1.5 rounded-lg inline-block text-center shadow-2xs">
                $50,000 / yr + usage
              </span>
            </div>

            {/* Card 3 */}
            <div className="p-6 rounded-2xl bg-[#F9F9F7] border border-gray-100 flex flex-col justify-between">
              <div>
                <span className="text-xs font-mono text-[#5A6B4A] font-semibold uppercase block mb-1">
                  Compliance Tier
                </span>
                <h3 className="font-serif text-lg text-gray-900 font-medium mb-2">
                  Indian & Global Exporters
                </h3>
                <p className="text-xs text-gray-600 leading-relaxed mb-4">
                  $10K–30K/year. Pre-submission validation to avoid costly EU rejections.
                </p>
              </div>
              <span className="text-xs font-semibold text-gray-900 bg-white border border-gray-200 px-3 py-1.5 rounded-lg inline-block text-center shadow-2xs">
                $10K – $30K / year
              </span>
            </div>
          </div>

          {/* Revenue Math banner */}
          <div className="bg-[#5A6B4A]/10 border border-[#5A6B4A]/20 rounded-2xl p-4 text-center">
            <p className="text-xs sm:text-sm font-semibold text-[#5A6B4A] tracking-wide">
              ⚡ 2 customers = $1M ARR • 97% gross margin • Breakeven at 1 customer
            </p>
          </div>
        </section>

        {/* SECTION 5 — MARKET OPPORTUNITY */}
        <section className="bg-white rounded-3xl p-8 sm:p-10 border border-gray-100 shadow-xs mb-8">
          <h2 className="font-serif text-2xl sm:text-3xl text-gray-900 mb-6 font-medium tracking-tight">
            The Market
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="p-5 bg-[#F9F9F7] rounded-2xl border border-gray-100">
              <div className="font-serif text-3xl sm:text-4xl text-gray-900 font-semibold mb-1">
                $1.2B
              </div>
              <p className="text-xs text-gray-500 font-medium leading-snug">
                EUDR software market (2025)
              </p>
            </div>
            <div className="p-5 bg-[#F9F9F7] rounded-2xl border border-gray-100">
              <div className="font-serif text-3xl sm:text-4xl text-gray-900 font-semibold mb-1">
                $1.8B
              </div>
              <p className="text-xs text-gray-500 font-medium leading-snug">
                Projected market by 2036
              </p>
            </div>
            <div className="p-5 bg-[#F9F9F7] rounded-2xl border border-gray-100">
              <div className="font-serif text-3xl sm:text-4xl text-[#5A6B4A] font-semibold mb-1">
                $6.8B
              </div>
              <p className="text-xs text-gray-500 font-medium leading-snug">
                Ocean plastic market (2034)
              </p>
            </div>
            <div className="p-5 bg-[#F9F9F7] rounded-2xl border border-gray-100">
              <div className="font-serif text-3xl sm:text-4xl text-[#5A6B4A] font-semibold mb-1">
                21.5%
              </div>
              <p className="text-xs text-gray-500 font-medium leading-snug">
                Ocean plastic CAGR growth
              </p>
            </div>
          </div>
        </section>

        {/* SECTION 6 — ROADMAP */}
        <section className="bg-white rounded-3xl p-8 sm:p-10 border border-gray-100 shadow-xs mb-8">
          <h2 className="font-serif text-2xl sm:text-3xl text-gray-900 mb-8 font-medium tracking-tight">
            What's Next
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 relative">
            {/* Milestone 1 */}
            <div className="p-5 bg-[#F9F9F7] rounded-2xl border border-gray-100 relative">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#5A6B4A] ring-4 ring-[#5A6B4A]/20"></span>
                <span className="font-mono text-xs font-semibold text-[#5A6B4A] uppercase">
                  Now
                </span>
              </div>
              <h3 className="text-sm font-semibold text-gray-900 mb-1">
                Hackathon Prototype
              </h3>
              <p className="text-xs text-gray-500 leading-relaxed">
                Live demo with full interactive satellite forensics and PDF dossier generation.
              </p>
            </div>

            {/* Milestone 2 */}
            <div className="p-5 bg-[#F9F9F7] rounded-2xl border border-gray-100 relative">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-stone-400"></span>
                <span className="font-mono text-xs font-semibold text-gray-700 uppercase">
                  Q1 2026
                </span>
              </div>
              <h3 className="text-sm font-semibold text-gray-900 mb-1">
                Earth Engine Pipeline
              </h3>
              <p className="text-xs text-gray-500 leading-relaxed">
                Connect real Google Earth Engine automated tile ingestion and SAR pipeline.
              </p>
            </div>

            {/* Milestone 3 */}
            <div className="p-5 bg-[#F9F9F7] rounded-2xl border border-gray-100 relative">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-stone-400"></span>
                <span className="font-mono text-xs font-semibold text-gray-700 uppercase">
                  Q2 2026
                </span>
              </div>
              <h3 className="text-sm font-semibold text-gray-900 mb-1">
                Enforcement Pilot
              </h3>
              <p className="text-xs text-gray-500 leading-relaxed">
                Execute enterprise pilot with 1 national EUDR enforcement agency.
              </p>
            </div>

            {/* Milestone 4 */}
            <div className="p-5 bg-[#F9F9F7] rounded-2xl border border-gray-100 relative">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-stone-400"></span>
                <span className="font-mono text-xs font-semibold text-gray-700 uppercase">
                  Q4 2026
                </span>
              </div>
              <h3 className="text-sm font-semibold text-gray-900 mb-1">
                Ocean Plastic (Phase 2)
              </h3>
              <p className="text-xs text-gray-500 leading-relaxed">
                Launch Sentinel-2 multispectral ocean plastic windrow detection engine.
              </p>
            </div>
          </div>
        </section>

        {/* SECTION 7 — CLOSING CTA */}
        <section className="bg-[#5A6B4A] rounded-3xl p-10 sm:p-14 text-center text-white shadow-lg">
          <h2 className="font-serif text-2xl sm:text-4xl lg:text-5xl font-medium tracking-tight max-w-2xl mx-auto leading-tight">
            We're not selling sustainability. We're selling fine avoidance.
          </h2>
          <p className="text-white/80 text-base sm:text-lg mt-3 max-w-xl mx-auto font-light">
            The forensic layer the EUDR market is missing.
          </p>
          <div className="mt-8">
            <Link
              to="/dashboard"
              className="inline-flex items-center justify-center bg-white text-[#5A6B4A] font-semibold text-sm px-8 py-3.5 rounded-full hover:bg-stone-100 transition-all shadow-md active:scale-95 cursor-pointer"
            >
              View Live Demo →
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
