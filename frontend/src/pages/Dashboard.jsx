import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import toast from 'react-hot-toast';
import { getFarms, analyze } from '../api/client';
import Map from '../components/Map';
import Navbar from '../components/Navbar';
import RiskChart from '../components/RiskChart';

export default function Dashboard() {
  const location = useLocation();

  // State
  const [farms, setFarms] = useState([]);
  const [selectedFarm, setSelectedFarm] = useState(null);
  const [coords, setCoords] = useState({ lat: -10.5124, lng: -62.2158 });
  const [dateStart, setDateStart] = useState('2023-01-01');
  const [dateEnd, setDateEnd] = useState('2024-01-01');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showPanel, setShowPanel] = useState(false);
  const [animatedScore, setAnimatedScore] = useState(0);

  // UI state
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Check if a farm was passed from navigation (e.g. from Farms table)
  useEffect(() => {
    if (location.state?.selectedFarm) {
      const incoming = location.state.selectedFarm;
      setSelectedFarm(incoming);
      setCoords({ lat: incoming.lat, lng: incoming.lng });
    }
  }, [location.state]);

  // Fetch farms on mount
  useEffect(() => {
    let isMounted = true;
    async function loadFarms() {
      try {
        const data = await getFarms();
        if (isMounted && data) {
          setFarms(data);
        }
      } catch (err) {
        toast.error('Could not load farms');
      }
    }
    loadFarms();
    return () => {
      isMounted = false;
    };
  }, []);

  // Animate risk score bar when result appears
  useEffect(() => {
    if (result && showPanel) {
      setAnimatedScore(0);
      const timer = setTimeout(() => {
        setAnimatedScore(result.score || 87);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      setAnimatedScore(0);
    }
  }, [result, showPanel]);

  // Handle analysis
  const handleAnalyze = async (e) => {
    e?.preventDefault();
    setLoading(true);

    try {
      // Build polygon from coords (small square, ±0.05 degrees)
      const lat = Number(coords.lat);
      const lng = Number(coords.lng);
      const polygon = [
        [lng - 0.05, lat - 0.05],
        [lng + 0.05, lat - 0.05],
        [lng + 0.05, lat + 0.05],
        [lng - 0.05, lat + 0.05],
        [lng - 0.05, lat - 0.05],
      ];

      const data = await analyze(polygon, dateStart, dateEnd);
      setResult(data);
      setShowPanel(true);
      toast.success('Analysis complete');
    } catch (err) {
      toast.error(err?.message || 'Analysis failed. Please retry.');
    } finally {
      setLoading(false);
    }
  };

  // Handle farm card click
  const handleSelectFarm = (farm) => {
    setSelectedFarm(farm);
    setCoords({ lat: farm.lat, lng: farm.lng });
  };

  // Handle alert card click
  const handleAlertClick = (alert) => {
    setCoords({ lat: alert.lat, lng: alert.lng });
    toast.success(`Focused alert at ${alert.lat.toFixed(2)}°, ${alert.lng.toFixed(2)}°`);
  };

  // Handle map click
  const handleMapClick = ({ lat, lng }) => {
    setCoords({
      lat: Number(lat.toFixed(4)),
      lng: Number(lng.toFixed(4)),
    });
  };

  // Helper for risk badge colors
  const getBadgeStyle = (status) => {
    switch (status) {
      case 'HIGH':
        return 'bg-red-50 text-red-700 border border-red-100';
      case 'MEDIUM':
        return 'bg-amber-50 text-amber-700 border border-amber-100';
      case 'OK':
      default:
        return 'bg-green-50 text-green-700 border border-green-100';
    }
  };

  // Helper for risk banner styling
  const getRiskBannerStyle = (risk) => {
    switch (risk) {
      case 'HIGH':
        return {
          wrapper: 'bg-red-50 border border-red-100',
          text: 'text-red-700',
          bar: 'bg-red-500',
        };
      case 'MEDIUM':
        return {
          wrapper: 'bg-amber-50 border border-amber-100',
          text: 'text-amber-700',
          bar: 'bg-amber-500',
        };
      case 'OK':
      default:
        return {
          wrapper: 'bg-green-50 border border-green-100',
          text: 'text-green-700',
          bar: 'bg-green-500',
        };
    }
  };

  const riskStyle = getRiskBannerStyle(result?.risk || 'HIGH');

  return (
    <div className="h-screen flex flex-col bg-[#F9F9F7] text-[#1A1A1A] font-sans selection:bg-[#5A6B4A]/20 overflow-hidden">
      {/* Reusable Navbar */}
      <Navbar activePage="dashboard" />

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Mobile sidebar toggle button */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="lg:hidden absolute top-4 left-4 z-30 p-2 bg-white rounded-full shadow-md text-gray-700 hover:bg-gray-50 border border-gray-200"
          aria-label="Toggle Sidebar"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        {/* LEFT SIDEBAR (w-80 bg-white border-r border-gray-200 flex flex-col overflow-y-auto) */}
        <aside
          className={`w-80 bg-white border-r border-gray-200 flex flex-col overflow-y-auto flex-shrink-0 z-20 transition-all duration-300 absolute lg:relative inset-y-0 left-0 shadow-lg lg:shadow-none ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
          }`}
        >
          {/* Section A — "Analyze Farm" (p-6 border-b) */}
          <div className="p-6 border-b border-gray-100">
            <h2 className="text-lg font-serif text-gray-900 mb-4 font-medium">
              Analyze Farm
            </h2>

            <form onSubmit={handleAnalyze}>
              {/* Coordinate inputs */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    Latitude
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={coords.lat}
                    onChange={(e) =>
                      setCoords((prev) => ({ ...prev, lat: parseFloat(e.target.value) || 0 }))
                    }
                    className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition-all"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    Longitude
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={coords.lng}
                    onChange={(e) =>
                      setCoords((prev) => ({ ...prev, lng: parseFloat(e.target.value) || 0 }))
                    }
                    className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition-all"
                  />
                </div>
              </div>

              {/* Helper text */}
              <p className="text-xs text-gray-400 italic mt-2">
                Or click anywhere on the map
              </p>

              {/* Date inputs */}
              <div className="space-y-3 mt-4">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={dateStart}
                    onChange={(e) => setDateStart(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition-all text-gray-700 font-sans"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={dateEnd}
                    onChange={(e) => setDateEnd(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition-all text-gray-700 font-sans"
                  />
                </div>
              </div>

              {/* Analyze Button */}
              <button
                type="submit"
                disabled={loading}
                className={`w-full mt-6 bg-[#5A6B4A] text-white py-3 rounded-full font-medium flex items-center justify-center gap-2 hover:bg-[#4a5a3d] transition-all duration-200 shadow-sm disabled:opacity-75 disabled:cursor-not-allowed ${
                  loading ? 'animate-pulse' : 'hover:scale-[1.01]'
                }`}
              >
                {loading ? (
                  <>
                    <svg
                      className="animate-spin h-4 w-4 text-white"
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
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <span>Analyze</span>
                    <span className="text-base leading-none font-bold">↗</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Section B — "Monitored Farms" (p-6 flex-1) */}
          <div className="p-6 flex-1">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                Monitored Farms
              </h3>
              <span className="text-xs text-gray-400 font-mono">
                {farms.length} tracked
              </span>
            </div>

            <div className="space-y-2">
              {farms.map((farm) => {
                const isSelected = selectedFarm?.id === farm.id;
                return (
                  <button
                    key={farm.id}
                    onClick={() => handleSelectFarm(farm)}
                    className={`w-full text-left p-3.5 rounded-xl border transition-all duration-200 cursor-pointer ${
                      isSelected
                        ? 'border-[#5A6B4A] ring-2 ring-[#5A6B4A] bg-[#F9F9F7]'
                        : 'border-gray-100 hover:border-[#5A6B4A]/30 hover:bg-[#F9F9F7] hover:scale-[1.01]'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900 truncate max-w-[170px]">
                        {farm.name}
                      </span>
                      <span
                        className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${getBadgeStyle(
                          farm.status
                        )}`}
                      >
                        {farm.status}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 flex items-center justify-between font-sans">
                      <span>{farm.loss}</span>
                      <span className="font-mono text-[11px] text-gray-400">
                        {farm.lat.toFixed(2)}°, {farm.lng.toFixed(2)}°
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Section: Risk Distribution Chart */}
          <div className="p-6 border-t border-gray-100 bg-white">
            <RiskChart />
          </div>

          {/* Section C — "Recent Alerts" */}
          <div className="p-6 border-t border-gray-100 bg-[#FBFBFA]">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider flex items-center gap-1.5">
                <span>🔴</span>
                <span>Recent Alerts</span>
              </h3>
              <span className="text-[10px] font-mono text-[#5A6B4A] font-semibold uppercase bg-[#5A6B4A]/10 px-2 py-0.5 rounded-full">
                LIVE
              </span>
            </div>

            <div className="space-y-2.5">
              {/* Alert 1 (Live Pulse) */}
              <button
                onClick={() => handleAlertClick({ lat: -10.5124, lng: -62.2158, name: 'Fazenda Santa Maria' })}
                className="w-full text-left p-3 bg-white rounded-xl border border-red-200/80 shadow-xs hover:border-red-400 hover:scale-[1.01] transition-all cursor-pointer group"
              >
                <div className="flex items-start gap-2.5">
                  <span className="relative flex h-2.5 w-2.5 mt-1">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-600"></span>
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-gray-900 leading-snug group-hover:text-red-700 transition-colors">
                      Forest loss detected at -10.51°, -62.22°
                    </p>
                    <div className="flex items-center justify-between mt-1 text-[11px] text-gray-400 font-mono">
                      <span>2 hours ago</span>
                      <span className="text-red-600 font-semibold uppercase text-[10px]">High Alert</span>
                    </div>
                  </div>
                </div>
              </button>

              {/* Alert 2 */}
              <button
                onClick={() => handleAlertClick({ lat: -10.4289, lng: -62.1542, name: 'Rancho Verde Norte' })}
                className="w-full text-left p-3 bg-white rounded-xl border border-gray-100 shadow-xs hover:border-amber-300 hover:scale-[1.01] transition-all cursor-pointer group"
              >
                <div className="flex items-start gap-2.5">
                  <span className="inline-flex rounded-full h-2.5 w-2.5 bg-amber-500 mt-1 flex-shrink-0"></span>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-gray-800 leading-snug group-hover:text-amber-700 transition-colors">
                      SAR coherence drop along corridor -10.43°, -62.15°
                    </p>
                    <div className="flex items-center justify-between mt-1 text-[11px] text-gray-400 font-mono">
                      <span>5 hours ago</span>
                      <span className="text-amber-600 font-semibold uppercase text-[10px]">Moderate</span>
                    </div>
                  </div>
                </div>
              </button>

              {/* Alert 3 */}
              <button
                onClick={() => handleAlertClick({ lat: -10.6311, lng: -62.3105, name: 'Agroflorestal Nova Vida' })}
                className="w-full text-left p-3 bg-white rounded-xl border border-gray-100 shadow-xs hover:border-amber-300 hover:scale-[1.01] transition-all cursor-pointer group"
              >
                <div className="flex items-start gap-2.5">
                  <span className="inline-flex rounded-full h-2.5 w-2.5 bg-amber-500 mt-1 flex-shrink-0"></span>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-gray-800 leading-snug group-hover:text-amber-700 transition-colors">
                      Boundary anomaly flagged near -10.63°, -62.31°
                    </p>
                    <div className="flex items-center justify-between mt-1 text-[11px] text-gray-400 font-mono">
                      <span>12 hours ago</span>
                      <span className="text-amber-600 font-semibold uppercase text-[10px]">Audit Req</span>
                    </div>
                  </div>
                </div>
              </button>

              {/* Alert 4 */}
              <button
                onClick={() => handleAlertClick({ lat: -10.3841, lng: -62.0917, name: 'Fazenda Rio Bonito' })}
                className="w-full text-left p-3 bg-white rounded-xl border border-gray-100 shadow-xs hover:border-emerald-300 hover:scale-[1.01] transition-all cursor-pointer group"
              >
                <div className="flex items-start gap-2.5">
                  <span className="inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500 mt-1 flex-shrink-0"></span>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-gray-800 leading-snug group-hover:text-emerald-700 transition-colors">
                      Full canopy compliance verified at -10.38°, -62.09°
                    </p>
                    <div className="flex items-center justify-between mt-1 text-[11px] text-gray-400 font-mono">
                      <span>1 day ago</span>
                      <span className="text-emerald-600 font-semibold uppercase text-[10px]">Verified</span>
                    </div>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </aside>


        {/* RIGHT AREA — MAP (flex-1 relative) */}
        <main className="flex-1 relative h-full w-full bg-stone-900">
          {/* Map Component */}
          <Map
            coords={coords}
            onMapClick={handleMapClick}
            deforestationResult={result}
            selectedFarm={selectedFarm}
          />

          {/* Floating Legend */}
          <div className="absolute bottom-6 left-6 z-20 bg-white/95 backdrop-blur-md rounded-2xl shadow-xl p-4 border border-gray-100 min-w-[190px] animate-fade-in pointer-events-auto">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-800 mb-3 font-sans">
              Legend
            </h4>
            <div className="space-y-2 text-xs text-gray-700">
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm" />
                <span>Compliant</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-red-600 shadow-sm" />
                <span>High Risk</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-sm" />
                <span>Medium Risk</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-4 h-0 border-t-2 border-dashed border-gray-700" />
                <span>Submitted boundary</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-sm bg-red-600/70 border border-red-700" />
                <span>Detected loss</span>
              </div>
            </div>
          </div>

          {/* SLIDING RESULTS PANEL */}
          <div
            className={`absolute top-6 right-6 w-96 max-w-[calc(100vw-3rem)] bg-white rounded-2xl shadow-2xl p-6 max-h-[calc(100vh-6rem)] overflow-y-auto z-30 border border-gray-100 transition-all duration-500 ease-out ${
              result && showPanel
                ? 'translate-x-0 opacity-100 pointer-events-auto'
                : 'translate-x-[120%] opacity-0 pointer-events-none'
            }`}
          >
            {/* Header Row */}
            <div className="flex items-center justify-between mb-5">
              <h3 className="font-serif text-xl text-gray-900 font-medium">
                Analysis Results
              </h3>
              <button
                onClick={() => setShowPanel(false)}
                className="w-8 h-8 rounded-full hover:bg-gray-100 text-gray-400 hover:text-gray-700 flex items-center justify-center text-lg font-bold transition-colors"
                aria-label="Close panel"
              >
                ✕
              </button>
            </div>

            {/* Risk Score Banner */}
            <div className={`rounded-2xl p-5 mb-5 ${riskStyle.wrapper}`}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs uppercase tracking-wider text-gray-500 font-semibold">
                  FRAUD RISK
                </span>
                <span className="text-xs font-mono text-gray-500">
                  {animatedScore}% confidence
                </span>
              </div>
              <div className={`text-3xl font-serif font-bold ${riskStyle.text} mb-3 tracking-tight`}>
                {result?.risk || 'HIGH'}
              </div>

              {/* Progress Bar with animated transition */}
              <div className="h-2 bg-white/80 rounded-full overflow-hidden shadow-inner">
                <div
                  className={`h-full ${riskStyle.bar} rounded-full transition-all duration-1000 ease-out`}
                  style={{ width: `${animatedScore}%` }}
                />
              </div>
            </div>

            {/* Two Stat Cards */}
            <div className="grid grid-cols-2 gap-3 mb-5">
              <div className="bg-[#F9F9F7] rounded-xl p-4 border border-gray-100 hover:scale-[1.02] transition-transform duration-200">
                <div className="text-xs text-gray-500 mb-1 font-medium">Hectares Lost</div>
                <div className="text-2xl font-serif text-gray-900 font-bold">
                  {result?.hectaresLost || '12.4 ha'}
                </div>
              </div>
              <div className="bg-[#F9F9F7] rounded-xl p-4 border border-gray-100 hover:scale-[1.02] transition-transform duration-200">
                <div className="text-xs text-gray-500 mb-1 font-medium">Manipulation Score</div>
                <div className="text-2xl font-serif text-gray-900 font-bold">
                  {result?.manipulationScore || '0.87'}
                </div>
              </div>
            </div>

            {/* Before / After Image Pair */}
            <div className="mb-5">
              <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
                Temporal Satellite Imagery
              </div>
              <div className="grid grid-cols-2 gap-3">
                {/* Before: 2023 */}
                <div className="relative aspect-square rounded-xl overflow-hidden shadow-sm hover:scale-105 transition-transform duration-300 group cursor-pointer bg-gradient-to-br from-emerald-900 via-green-800 to-emerald-950 flex items-center justify-center">
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.3)_0%,transparent_70%)]" />
                  <span className="text-emerald-100 text-xs font-mono font-medium z-10 opacity-80 group-hover:opacity-100">
                    Intact Canopy
                  </span>
                  <div className="absolute bottom-2 left-2 bg-black/60 backdrop-blur text-white text-[11px] font-mono px-2 py-0.5 rounded-full z-10">
                    2023
                  </div>
                </div>

                {/* After: 2024 */}
                <div className="relative aspect-square rounded-xl overflow-hidden shadow-sm hover:scale-105 transition-transform duration-300 group cursor-pointer bg-gradient-to-br from-red-950 via-rose-900 to-amber-950 flex items-center justify-center">
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(239,68,68,0.4)_0%,transparent_70%)]" />
                  <span className="text-rose-100 text-xs font-mono font-medium z-10 opacity-80 group-hover:opacity-100">
                    Forest Loss
                  </span>
                  <div className="absolute bottom-2 left-2 bg-black/60 backdrop-blur text-white text-[11px] font-mono px-2 py-0.5 rounded-full z-10">
                    2024
                  </div>
                </div>
              </div>
            </div>

            {/* Evidence Summary */}
            <div className="bg-[#F9F9F7] rounded-xl p-4 mb-5 border border-gray-100">
              <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-800 mb-2.5 font-sans">
                Evidence Summary
              </h4>
              <ul className="space-y-2">
                {(result?.evidence || [
                  'Satellite SAR coherence drops 42% along southwest forest corridor.',
                  'Spectral analysis reveals illegal burn clearance conducted post-cut-off date.',
                  'Cadastral property boundary overlaps directly with designated conservation polygon.'
                ]).map((item, idx) => (
                  <li key={idx} className="text-xs text-gray-600 leading-relaxed flex gap-2 items-start">
                    <span className="text-[#5A6B4A] font-bold text-sm leading-none mt-0.5">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Download PDF button */}
            <button
              onClick={() => toast.success('PDF EUDR Compliance Report generated')}
              className="w-full bg-[#5A6B4A] text-white py-3 rounded-full font-medium flex items-center justify-center gap-2 hover:bg-[#4a5a3d] transition-all duration-200 shadow-sm text-sm active:scale-[0.99]"
            >
              <span>Download PDF Report</span>
              <span className="text-base font-bold">↗</span>
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}
