import React from 'react';
import toast from 'react-hot-toast';
import Navbar from '../components/Navbar';

export default function Ocean() {
  const handleJoinWaitlist = () => {
    toast.success("You're on the list!");
  };

  const steps = [
    'Sentinel-2 multispectral analysis of ocean surface',
    'Identifies plastic windrows (dense floating patches)',
    'Matches hotspots with local cleanup vessels',
    'Blockchain-verified plastic recovery credits',
  ];

  const whyNowPoints = [
    "The EU's Plastic Strategy mandates 30% recycled content by 2030",
    "Voluntary plastic credits market already trading at $200-800/tonne",
    "Same satellite engine as deforestation — zero new R&D",
  ];

  const competitors = [
    {
      company: 'Recyclux',
      whatTheyDo: 'Satellite detection + cleanup coordination',
      ourEdge: 'We own the fraud-detection layer',
    },
    {
      company: 'Plastic-i',
      whatTheyDo: 'Ocean intelligence platform',
      ourEdge: 'We already have EUDR compliance customers',
    },
    {
      company: 'Seven Clean Seas',
      whatTheyDo: 'Plastic credit verification',
      ourEdge: 'We verify the source, not just the cleanup',
    },
  ];

  const roadmap = [
    {
      quarter: 'Q1 2026',
      title: 'Pilot with 1 cleanup org',
      description: 'Deploy real-time detection pipeline with active marine recovery partners.',
    },
    {
      quarter: 'Q2 2026',
      title: 'Launch plastic credit API',
      description: 'Automated verification & tokenized audit trail for EPR credits.',
    },
    {
      quarter: 'Q3 2026',
      title: '5 corporate customers',
      description: 'Expand enterprise compliance for EU packaging directive mandates.',
    },
    {
      quarter: 'Q4 2026',
      title: '$500K ARR',
      description: 'Recurring satellite monitoring contracts & verified plastic certification fees.',
    },
  ];

  const marketStats = [
    {
      stat: '$1.2B',
      label: 'Plastic credits market (2025)',
    },
    {
      stat: '$6.8B',
      label: 'Projected by 2034',
    },
    {
      stat: '21.5%',
      label: 'CAGR',
    },
    {
      stat: 'Proven',
      label: 'By Recyclux, Plastic-i',
    },
  ];

  return (
    <div className="min-h-screen bg-[#F9F9F7] text-[#1A1A1A] font-sans selection:bg-[#5A6B4A]/20 flex flex-col">
      {/* Top Navbar */}
      <Navbar activePage="ocean" />

      {/* Main Container */}
      <main className="max-w-4xl w-full mx-auto px-6 sm:px-8 py-16 flex-1">
        {/* HERO SECTION */}
        <div className="rounded-3xl overflow-hidden relative mb-12 h-96 shadow-lg">
          {/* Background Image */}
          <img
            src="https://images.unsplash.com/photo-1621451537084-482c73073a0f?auto=format&fit=crop&w=1600&q=80"
            alt="Ocean Plastic Satellite Analysis"
            className="w-full h-full object-cover"
          />

          {/* Dark Overlay */}
          <div className="absolute inset-0 bg-[#0F172A]/60 backdrop-blur-[1px]" />

          {/* Hero Content */}
          <div className="absolute inset-0 p-8 sm:p-12 text-center flex flex-col items-center justify-center z-10">
            <span className="text-xs tracking-widest text-white/80 mb-4 uppercase font-semibold">
              PHASE 2 ROADMAP
            </span>
            <h1 className="font-serif text-3xl sm:text-5xl text-white leading-tight font-medium max-w-2xl">
              Same engine. Different environment.
            </h1>
            <p className="text-white/80 mt-4 max-w-lg text-base sm:text-lg font-normal leading-relaxed">
              Extending TerraWatch satellite detection to ocean plastic mapping
            </p>
          </div>
        </div>

        {/* 1. VISUAL PROOF SECTION */}
        <section className="mb-12 bg-white rounded-3xl p-8 sm:p-10 shadow-sm border border-gray-100">
          <div className="mb-6">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#5A6B4A]">
              Spectral Verification
            </span>
            <h2 className="font-serif text-2xl text-gray-900 font-medium mt-1">
              What It Looks Like in Practice
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            {/* Left Column: Raw Satellite Optical Feed */}
            <div className="relative rounded-2xl overflow-hidden border border-gray-200 aspect-4/3 group shadow-xs">
              <img
                src="https://images.unsplash.com/photo-1621451537084-482c73073a0f?auto=format&fit=crop&w=800&q=80"
                alt="Raw Satellite Optical Feed"
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute bottom-3 left-3 bg-black/70 backdrop-blur-xs text-white text-xs font-mono px-3 py-1 rounded-full">
                Sentinel-2 Optical (RGB)
              </div>
            </div>

            {/* Right Column: Detected Plastic Windrows Overlay */}
            <div className="relative rounded-2xl overflow-hidden border border-amber-200 aspect-4/3 group shadow-xs bg-slate-900">
              <img
                src="https://images.unsplash.com/photo-1621451537084-482c73073a0f?auto=format&fit=crop&w=800&q=80"
                alt="Detected plastic windrows overlay"
                className="w-full h-full object-cover opacity-60 contrast-125 saturate-50"
              />
              {/* Yellow Spectral Hotspot Overlay */}
              <div className="absolute inset-0 bg-radial from-amber-400/30 via-yellow-500/20 to-transparent pointer-events-none" />
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                <polygon
                  points="90,70 190,50 250,110 180,160 110,130"
                  fill="rgba(251, 191, 36, 0.45)"
                  stroke="#FBBF24"
                  strokeWidth="2.5"
                  strokeDasharray="6,4"
                  className="animate-pulse"
                />
                <circle cx="160" cy="100" r="28" fill="#FBBF24" fillOpacity="0.25" />
                <text
                  x="160"
                  y="105"
                  fill="#FFFFFF"
                  fontSize="11"
                  fontWeight="bold"
                  textAnchor="middle"
                  fontFamily="monospace"
                >
                  WINDROW DETECTED
                </text>
              </svg>

              <div className="absolute top-3 left-3 bg-amber-500/90 backdrop-blur-xs text-slate-950 text-xs font-bold px-3 py-1 rounded-full shadow-sm">
                AI Detection Mask
              </div>
              <div className="absolute bottom-3 left-3 right-3 bg-black/80 backdrop-blur-xs text-amber-200 text-xs px-3.5 py-2 rounded-xl border border-amber-500/30">
                <span className="font-semibold text-white">Detected plastic windrows:</span> Sentinel-2 multispectral analysis highlights plastic patches in yellow.
              </div>
            </div>
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section className="mb-12">
          <h2 className="font-serif text-2xl text-gray-900 mb-6 font-medium">
            How It Works
          </h2>
          <div className="space-y-4 bg-white rounded-3xl p-8 sm:p-10 shadow-sm border border-gray-100">
            {steps.map((step, idx) => (
              <div key={idx} className="flex gap-4 items-start">
                <span className="w-2.5 h-2.5 rounded-full bg-[#5A6B4A] mt-2.5 flex-shrink-0" />
                <p className="text-gray-600 text-base sm:text-lg leading-relaxed">
                  {step}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* 2. WHY NOW SECTION */}
        <section className="mb-12 bg-white rounded-3xl p-8 sm:p-10 shadow-sm border border-gray-100">
          <div className="mb-6">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#5A6B4A]">
              Urgency & Catalysts
            </span>
            <h2 className="font-serif text-2xl text-gray-900 font-medium mt-1">
              Why Ocean Plastic, Why Now
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {whyNowPoints.map((point, idx) => (
              <div
                key={idx}
                className="bg-[#F9F9F7] rounded-2xl p-6 border border-gray-100 flex flex-col justify-between hover:border-[#5A6B4A]/30 transition-colors"
              >
                <div className="text-2xl font-serif font-bold text-[#5A6B4A] mb-3">
                  0{idx + 1}
                </div>
                <p className="text-gray-700 text-sm font-medium leading-relaxed">
                  {point}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* 3. COMPETITIVE LANDSCAPE */}
        <section className="mb-12 bg-white rounded-3xl p-8 sm:p-10 shadow-sm border border-gray-100 overflow-hidden">
          <div className="mb-6">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#5A6B4A]">
              Strategic Differentiation
            </span>
            <h2 className="font-serif text-2xl text-gray-900 font-medium mt-1">
              Competitive Landscape
            </h2>
          </div>

          <div className="overflow-x-auto -mx-8 sm:-mx-10 px-8 sm:px-10">
            <table className="w-full text-left border-collapse min-w-[500px]">
              <thead>
                <tr className="border-b border-gray-200 text-xs font-semibold uppercase tracking-wider text-gray-400">
                  <th className="pb-3.5 pr-4">Company</th>
                  <th className="pb-3.5 px-4">What They Do</th>
                  <th className="pb-3.5 pl-4 text-[#5A6B4A]">Our Edge</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-sm">
                {competitors.map((c, idx) => (
                  <tr key={idx} className="hover:bg-[#F9F9F7]/70 transition-colors">
                    <td className="py-4 pr-4 font-serif font-semibold text-gray-900 text-base">
                      {c.company}
                    </td>
                    <td className="py-4 px-4 text-gray-600">
                      {c.whatTheyDo}
                    </td>
                    <td className="py-4 pl-4 font-medium text-[#5A6B4A]">
                      <span className="inline-flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#5A6B4A]"></span>
                        {c.ourEdge}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* MARKET SECTION */}
        <section className="bg-white rounded-3xl p-8 sm:p-10 mb-12 shadow-sm border border-gray-100">
          <h2 className="font-serif text-2xl text-gray-900 mb-8 font-medium">
            Market Opportunity
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {marketStats.map((item, idx) => (
              <div key={idx} className="flex flex-col items-center justify-center">
                <div className="font-serif text-3xl sm:text-4xl text-[#5A6B4A] font-bold tracking-tight">
                  {item.stat}
                </div>
                <div className="text-xs text-gray-500 mt-2 uppercase tracking-wide font-medium leading-normal">
                  {item.label}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 4. ROADMAP TIMELINE */}
        <section className="bg-white rounded-3xl p-8 sm:p-10 mb-12 shadow-sm border border-gray-100">
          <div className="mb-8 text-center sm:text-left">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#5A6B4A]">
              Execution Horizon
            </span>
            <h2 className="font-serif text-2xl text-gray-900 font-medium mt-1">
              Roadmap Timeline
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 relative">
            {roadmap.map((m, idx) => (
              <div
                key={idx}
                className="bg-[#F9F9F7] rounded-2xl p-5 border border-gray-200/80 flex flex-col justify-between relative group hover:border-[#5A6B4A] hover:shadow-sm transition-all"
              >
                <div>
                  <div className="inline-block bg-[#5A6B4A] text-white text-xs font-bold px-3 py-1 rounded-full mb-3 shadow-xs">
                    {m.quarter}
                  </div>
                  <h3 className="font-serif text-base font-semibold text-gray-900 mb-1.5">
                    {m.title}
                  </h3>
                  <p className="text-gray-500 text-xs leading-relaxed">
                    {m.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* STATUS BANNER */}
        <section className="bg-[#F9F9F7] border border-gray-200 rounded-3xl p-8 sm:p-10 text-center shadow-xs">
          <p className="text-sm font-medium text-gray-500 mb-6 uppercase tracking-wider">
            🔬 Research Phase — Not part of the 24-hour hackathon build
          </p>
          <button
            onClick={handleJoinWaitlist}
            className="inline-flex items-center justify-center bg-[#5A6B4A] text-white px-10 py-4 rounded-full text-sm font-medium hover:bg-[#4a5a3d] transition-all duration-200 shadow-md hover:shadow-lg active:scale-95 gap-2"
          >
            <span>Join Waitlist</span>
            <span className="text-base font-bold">↗</span>
          </button>
        </section>
      </main>
    </div>
  );
}
