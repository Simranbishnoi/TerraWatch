import React, { useState, useEffect, useRef } from 'react';

// Attempt to load react-map-gl if available in environment
let ReactMapGL = null;
let Source = null;
let Layer = null;
let Marker = null;

try {
  const mapgl = require('react-map-gl');
  ReactMapGL = mapgl.default || mapgl.Map || mapgl;
  Source = mapgl.Source;
  Layer = mapgl.Layer;
  Marker = mapgl.Marker;
} catch (e) {
  // Graceful handling if module resolution is dynamic
}

export default function Map({
  coords = { lat: -10.5, lng: -62.2 },
  onMapClick,
  deforestationResult,
  selectedFarm,
}) {
  const [mapStyleType, setMapStyleType] = useState('satellite'); // 'satellite' | 'streets'
  const [viewState, setViewState] = useState({
    longitude: coords.lng,
    latitude: coords.lat,
    zoom: 10,
  });
  const [token, setToken] = useState(() => {
    return (
      (typeof import.meta !== 'undefined' &&
        import.meta.env &&
        import.meta.env.VITE_MAPBOX_TOKEN) ||
      (typeof window !== 'undefined' && window.mapboxToken) ||
      ''
    );
  });

  const mapRef = useRef(null);

  // Sync coords changes with map flyTo
  useEffect(() => {
    setViewState((prev) => ({
      ...prev,
      longitude: coords.lng,
      latitude: coords.lat,
      zoom: 11,
    }));
    if (mapRef.current) {
      mapRef.current.flyTo?.({
        center: [coords.lng, coords.lat],
        zoom: 11,
        duration: 1500,
      });
    }
  }, [coords]);

  const mapStyleUrl =
    mapStyleType === 'satellite'
      ? 'mapbox://styles/mapbox/satellite-streets-v12'
      : 'mapbox://styles/mapbox/outdoors-v12';

  const toggleStyle = () => {
    setMapStyleType((prev) => (prev === 'satellite' ? 'streets' : 'satellite'));
  };

  // If token is missing, render an interactive high-resolution satellite canvas mockup
  // that supports clicking anywhere, placing markers, toggling styles, and rendering the pulsing deforestation loss polygon.
  const renderFallbackMap = () => {
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
        {/* Satellite Background */}
        <img
          src="https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?auto=format&fit=crop&w=2000&q=80"
          alt="Satellite View"
          className={`w-full h-full object-cover transition-opacity duration-500 ${
            mapStyleType === 'satellite' ? 'opacity-80 contrast-125' : 'opacity-40 invert'
          }`}
        />

        {/* Ambient Grid overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff0a_1px,transparent_1px),linear-gradient(to_bottom,#ffffff0a_1px,transparent_1px)] bg-[size:4rem_4rem] pointer-events-none" />

        {/* Submitted Cadastral Boundary (White dashed polygon) */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <svg className="w-full h-full absolute inset-0">
            {/* Submitted boundary */}
            <polygon
              points="450,220 620,200 680,360 510,410 420,310"
              fill="none"
              stroke="#FFFFFF"
              strokeWidth="2"
              strokeDasharray="6,4"
              className="drop-shadow-md"
            />
            {/* Deforestation Loss Area (Pulsing Red Fill) */}
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

        {/* Center Target / Active Selected Marker */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none flex flex-col items-center">
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

        {/* Status watermark / attribution */}
        <div className="absolute bottom-2 right-4 text-[10px] text-white/60 bg-black/40 backdrop-blur px-2.5 py-1 rounded-md font-mono pointer-events-none">
          Lat: {coords.lat.toFixed(4)}° | Lng: {coords.lng.toFixed(4)}° | Zoom: 10x
        </div>
      </div>
    );
  };

  return (
    <div className="relative w-full h-full overflow-hidden">
      {/* Map Control Toggle (Satellite / Terrain Streets) */}
      <div className="absolute top-6 right-6 z-20">
        <button
          onClick={toggleStyle}
          title="Toggle Map Style"
          className="flex items-center gap-1.5 bg-white/95 backdrop-blur hover:bg-gray-50 text-gray-800 text-xs font-medium px-3.5 py-2 rounded-full shadow-md border border-gray-200/80 transition-all duration-200 active:scale-95"
        >
          <span>{mapStyleType === 'satellite' ? '🛰️ Satellite' : '🗺️ Terrain'}</span>
        </button>
      </div>

      {/* Map Container: Render Mapbox if token exists and ReactMapGL is loaded, else render interactive fallback */}
      {token && ReactMapGL ? (
        <ReactMapGL
          ref={mapRef}
          {...viewState}
          onMove={(evt) => setViewState(evt.viewState)}
          mapStyle={mapStyleUrl}
          mapboxAccessToken={token}
          style={{ width: '100%', height: '100%' }}
          onClick={(e) => {
            if (onMapClick && e.lngLat) {
              onMapClick({ lat: e.lngLat.lat, lng: e.lngLat.lng });
            }
          }}
        >
          {Marker && (
            <Marker longitude={coords.lng} latitude={coords.lat} anchor="bottom">
              <div className="relative flex flex-col items-center">
                <span className="animate-ping absolute inline-flex h-8 w-8 rounded-full bg-[#5A6B4A] opacity-60"></span>
                <div className="w-6 h-6 rounded-full bg-[#5A6B4A] border-2 border-white shadow-lg flex items-center justify-center text-xs text-white">
                  🛰️
                </div>
              </div>
            </Marker>
          )}

          {deforestationResult?.lossGeoJson && Source && Layer && (
            <Source id="deforestation-loss" type="geojson" data={deforestationResult.lossGeoJson}>
              <Layer
                id="deforestation-loss-fill"
                type="fill"
                paint={{
                  'fill-color': '#DC2626',
                  'fill-opacity': 0.5,
                }}
              />
              <Layer
                id="deforestation-loss-line"
                type="line"
                paint={{
                  'line-color': '#FFFFFF',
                  'line-width': 2,
                  'line-dasharray': [2, 2],
                }}
              />
            </Source>
          )}
        </ReactMapGL>
      ) : (
        renderFallbackMap()
      )}
    </div>
  );
}
