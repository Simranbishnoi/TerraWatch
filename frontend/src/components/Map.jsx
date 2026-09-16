import React from 'react';

export default function Map({
  coords = { lat: -10.5, lng: -62.2 },
  onMapClick,
  deforestationResult,
  selectedFarm,
}) {
  return (
    <div
      onClick={(e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;
        // Approximate coordinate map offset around Rondônia: [-62.2, -10.5]
        const newLng = Number((-62.35 + x * 0.3).toFixed(4));
        const newLat = Number((-10.35 - y * 0.3).toFixed(4));
        onMapClick?.({ lat: newLat, lng: newLng });
      }}
      className="relative w-full h-full cursor-crosshair overflow-hidden select-none bg-slate-900"
    >
      {/* 2. Background image of satellite map */}
      <img
        src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop"
        alt="Satellite View"
        className="w-full h-full object-cover opacity-90 contrast-110 pointer-events-none"
      />

      {/* 3. Dark overlay */}
      <div className="absolute inset-0 bg-black/20 pointer-events-none" />

      {/* Ambient Grid overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff0a_1px,transparent_1px),linear-gradient(to_bottom,#ffffff0a_1px,transparent_1px)] bg-[size:4rem_4rem] pointer-events-none" />

      {/* 4. Text in center */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
        <h2 className="text-white text-3xl md:text-4xl lg:text-5xl font-serif tracking-wide drop-shadow-lg opacity-80" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
          Amazon Rainforest - Rondônia Region
        </h2>
      </div>

      {/* 5. Legend, red polygons, and white dashed boundary */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
        <svg className="w-full h-full absolute inset-0">
          {/* White dashed boundary */}
          <polygon
            points="450,220 620,200 680,360 510,410 420,310"
            fill="none"
            stroke="#FFFFFF"
            strokeWidth="2"
            strokeDasharray="6,4"
            className="drop-shadow-md"
          />
          {/* Deforestation Loss Area (Red polygons) */}
          {deforestationResult && (
            <g className="animate-pulse-overlay">
              <polygon
                points="470,240 600,220 650,330 520,380 440,290"
                fill="rgba(220, 38, 38, 0.55)"
                stroke="#DC2626"
                strokeWidth="1.5"
              />
              <circle cx="560" cy="300" r="14" fill="#DC2626" fillOpacity="0.4" />
              <text
                x="560"
                y="304"
                fill="#ffffff"
                fontSize="11"
                fontWeight="bold"
                textAnchor="middle"
                className="font-mono drop-shadow"
              >
                LOSS: {deforestationResult.hectaresLost || '12.4 ha'}
              </text>
            </g>
          )}
        </svg>
      </div>

      {/* Map Marker Pin */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none flex flex-col items-center z-20">
        <div className="relative flex items-center justify-center">
          <span className="animate-ping absolute inline-flex h-8 w-8 rounded-full bg-[#5A6B4A] opacity-60"></span>
          <div className="w-5 h-5 rounded-full bg-[#5A6B4A] border-2 border-white shadow-xl flex items-center justify-center text-[10px] text-white font-bold">
            🛰️
          </div>
        </div>
        <div className="mt-1 bg-black/75 backdrop-blur text-white text-[11px] font-mono px-2 py-0.5 rounded-full border border-white/20 whitespace-nowrap shadow-md">
          {coords.lat.toFixed(4)}, {coords.lng.toFixed(4)}
        </div>
      </div>

      {/* Active Loss Banner if Deforestation Detected */}
      {deforestationResult && (
        <div className="absolute top-6 left-6 z-20 bg-red-600/90 backdrop-blur text-white text-xs font-semibold px-3.5 py-1.5 rounded-full shadow-lg flex items-center gap-2 font-mono">
          <span className="w-2 h-2 rounded-full bg-white animate-ping" />
          <span>LOSS DETECTED: {deforestationResult.hectaresLost || '12.4 ha'}</span>
        </div>
      )}

      {/* Floating Legend */}
      <div className="absolute bottom-6 left-6 z-20 bg-white/95 backdrop-blur-md rounded-2xl shadow-xl p-4 border border-gray-100 min-w-[190px]">
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

      {/* Coordinates watermark overlay */}
      <div className="absolute bottom-3 right-6 text-[10px] text-white/80 bg-black/60 backdrop-blur px-2.5 py-1 rounded-md font-mono pointer-events-none z-10 shadow-sm border border-white/10">
        Lat: {coords?.lat ? coords.lat.toFixed(4) : '-10.5000'}° | Lng:{' '}
        {coords?.lng ? coords.lng.toFixed(4) : '-62.2000'}° | Zoom: 10x
      </div>
    </div>
  );
}
