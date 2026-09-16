import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const DATA = [
  { name: 'Compliant (OK)', value: 835, color: '#16A34A', shortName: 'OK' },
  { name: 'Medium Risk', value: 8, color: '#F59E0B', shortName: 'Medium' },
  { name: 'High Risk', value: 4, color: '#DC2626', shortName: 'High' },
];

const TOTAL_COUNT = 847;

export default function RiskChart() {
  return (
    <div className="bg-white rounded-2xl p-4 border border-gray-100 shadow-xs">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-xs font-semibold text-gray-900 uppercase tracking-wider">
          Risk Distribution
        </h4>
        <span className="text-[11px] font-mono text-gray-400">EUDR Registry</span>
      </div>

      {/* Donut Chart Container */}
      <div className="relative h-44 w-full flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-[#1A1A1A] text-white text-xs px-2.5 py-1.5 rounded-lg shadow-lg">
                      <span className="font-semibold">{data.name}:</span> {data.value} farms
                    </div>
                  );
                }
                return null;
              }}
            />
            <Pie
              data={DATA}
              cx="50%"
              cy="50%"
              innerRadius={52}
              outerRadius={68}
              paddingAngle={3}
              dataKey="value"
              strokeWidth={0}
            >
              {DATA.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        {/* Center Total Count Overlay */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="font-serif text-2xl font-semibold text-gray-900 leading-none">
            {TOTAL_COUNT}
          </span>
          <span className="text-[10px] uppercase font-medium text-gray-400 tracking-wider mt-0.5">
            Total Farms
          </span>
        </div>
      </div>

      {/* Minimal Legend / Breakdown Pills */}
      <div className="grid grid-cols-3 gap-1.5 pt-2 border-t border-gray-50 text-center">
        <div className="bg-green-50/70 border border-green-100/60 rounded-xl py-1.5 px-1">
          <span className="block text-xs font-bold text-green-700 font-mono">835</span>
          <span className="text-[10px] text-green-800 font-medium">OK</span>
        </div>
        <div className="bg-amber-50/70 border border-amber-100/60 rounded-xl py-1.5 px-1">
          <span className="block text-xs font-bold text-amber-700 font-mono">8</span>
          <span className="text-[10px] text-amber-800 font-medium">Medium</span>
        </div>
        <div className="bg-red-50/70 border border-red-100/60 rounded-xl py-1.5 px-1">
          <span className="block text-xs font-bold text-red-700 font-mono">4</span>
          <span className="text-[10px] text-red-800 font-medium">High</span>
        </div>
      </div>
    </div>
  );
}
