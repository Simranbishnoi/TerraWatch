import React, { useState } from 'react';

export default function AddFarmModal({ isOpen, onClose, onFarmAdded }) {
  const [name, setName] = useState('');
  const [latitude, setLatitude] = useState('-10.5124');
  const [longitude, setLongitude] = useState('-62.2158');
  const [status, setStatus] = useState('HIGH');
  const [hectaresLost, setHectaresLost] = useState('12.4');
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;

    setSubmitting(true);
    try {
      await onFarmAdded({
        name: name.trim(),
        latitude: parseFloat(latitude) || 0,
        longitude: parseFloat(longitude) || 0,
        status,
        hectares_lost: parseFloat(hectaresLost) || 0,
      });
      // Reset form and close
      setName('');
      setLatitude('-10.5124');
      setLongitude('-62.2158');
      setStatus('HIGH');
      setHectaresLost('12.4');
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs animate-fade-in">
      <div
        className="bg-white rounded-3xl shadow-2xl border border-gray-100 max-w-lg w-full p-8 relative overflow-hidden transition-all duration-300"
        style={{ backgroundColor: '#FFFFFF' }}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 text-gray-400 hover:text-gray-700 w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-100 transition-colors"
          aria-label="Close modal"
        >
          ✕
        </button>

        {/* Modal Header */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-[#5A6B4A]"></span>
            <span className="text-xs font-semibold uppercase tracking-wider text-[#5A6B4A]">
              Cadastral Ingestion
            </span>
          </div>
          <h2 className="font-serif text-2xl sm:text-3xl text-gray-900 font-medium tracking-tight">
            Add Monitored Farm
          </h2>
          <p className="text-gray-500 text-xs sm:text-sm mt-1">
            Register a new agricultural plot for EUDR deforestation verification.
          </p>
        </div>

        {/* Modal Form */}
        <form onSubmit={handleSubmit} className="space-y-4 font-sans text-sm">
          {/* Farm Name */}
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
              Farm Name
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Fazenda Santa Maria"
              className="w-full px-4 py-3 bg-[#F9F9F7] border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition"
            />
          </div>

          {/* Coordinates Grid */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
                Latitude
              </label>
              <input
                type="number"
                step="any"
                required
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                placeholder="-10.5124"
                className="w-full px-4 py-3 bg-[#F9F9F7] border border-gray-200 rounded-xl text-gray-900 font-mono text-xs focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
                Longitude
              </label>
              <input
                type="number"
                step="any"
                required
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                placeholder="-62.2158"
                className="w-full px-4 py-3 bg-[#F9F9F7] border border-gray-200 rounded-xl text-gray-900 font-mono text-xs focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition"
              />
            </div>
          </div>

          {/* Status & Hectares Lost */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
                Status
              </label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-full px-4 py-3 bg-[#F9F9F7] border border-gray-200 rounded-xl text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition"
              >
                <option value="HIGH">HIGH (Deforestation Alert)</option>
                <option value="MEDIUM">MEDIUM (Suspect Border)</option>
                <option value="OK">OK (Compliant)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
                Hectares Lost
              </label>
              <input
                type="number"
                step="any"
                min="0"
                required
                value={hectaresLost}
                onChange={(e) => setHectaresLost(e.target.value)}
                placeholder="12.4"
                className="w-full px-4 py-3 bg-[#F9F9F7] border border-gray-200 rounded-xl text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition"
              />
            </div>
          </div>

          {/* Submit and Cancel buttons */}
          <div className="pt-4 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 rounded-full text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="inline-flex items-center justify-center bg-[#5A6B4A] text-white px-7 py-2.5 rounded-full text-sm font-medium hover:bg-[#4a5a3d] transition-all duration-200 shadow-sm active:scale-95 gap-2 disabled:opacity-50"
            >
              <span>{submitting ? 'Adding...' : 'Add Farm'}</span>
              <span className="text-base font-bold">↗</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
