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

        {/* CONTENT SECTION */}
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
