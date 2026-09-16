import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { getFarms } from '../api/client';
import Navbar from '../components/Navbar';

export default function Farms() {
  const [farms, setFarms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortField, setSortField] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc'); // 'asc' | 'desc'
  const navigate = useNavigate();

  // Load farms on mount
  useEffect(() => {
    let isMounted = true;
    async function load() {
      try {
        const data = await getFarms();
        if (isMounted) {
          setFarms(data || []);
        }
      } catch (err) {
        toast.error('Failed to load farms');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    load();
    return () => {
      isMounted = false;
    };
  }, []);

  // Filter & Sort
  const filteredFarms = useMemo(() => {
    let result = farms.filter((f) =>
      f.name.toLowerCase().includes(search.trim().toLowerCase())
    );

    result.sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];

      if (sortField === 'areaHa') {
        aVal = a.areaHa ?? (parseFloat(a.loss) || 0);
        bVal = b.areaHa ?? (parseFloat(b.loss) || 0);
      }

      if (typeof aVal === 'string') {
        return sortOrder === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
    });

    return result;
  }, [farms, search, sortField, sortOrder]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const handleRowClick = (farm) => {
    // Navigate to dashboard with selected farm
    navigate('/dashboard', { state: { selectedFarm: farm } });
  };

  const handleAddFarm = () => {
    toast.success('Cadastral parcel ingestion wizard opening...');
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'HIGH':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-100 shadow-xs">
            HIGH
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-100 shadow-xs">
            MEDIUM
          </span>
        );
      case 'OK':
      default:
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-50 text-green-700 border border-green-100 shadow-xs">
            OK
          </span>
        );
    }
  };

  return (
    <div className="min-h-screen bg-[#F9F9F7] text-[#1A1A1A] font-sans selection:bg-[#5A6B4A]/20 flex flex-col">
      {/* Top Navbar */}
      <Navbar activePage="farms" />

      {/* Main Content */}
      <main className="max-w-6xl w-full mx-auto px-6 sm:px-8 py-12 flex-1">
        {/* Header Section */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
          <div>
            <h1 className="font-serif text-3xl sm:text-4xl text-gray-900 font-medium tracking-tight">
              Monitored Farms
            </h1>
            <p className="text-gray-500 text-sm mt-1">
              847 total farms tracked across the Amazon region
            </p>
          </div>
          <div>
            <button
              onClick={handleAddFarm}
              className="inline-flex items-center justify-center bg-[#5A6B4A] text-white px-6 py-2.5 rounded-full text-sm font-medium hover:bg-[#4a5a3d] transition-all duration-200 shadow-sm active:scale-95 gap-1.5"
            >
              <span>+ Add Farm</span>
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative mb-6 max-w-md">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search farms by name..."
            className="w-full pl-11 pr-4 py-3 bg-white border border-gray-200 rounded-full text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#5A6B4A] focus:border-transparent transition-all shadow-xs"
          />
          <svg
            className="w-4 h-4 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-xs"
            >
              Clear
            </button>
          )}
        </div>

        {/* Data Table Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200/80 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#F9F9F7] border-b border-gray-200">
                  <th
                    onClick={() => handleSort('name')}
                    className="w-1/3 text-xs font-semibold uppercase tracking-wider text-gray-500 px-6 py-4 cursor-pointer hover:text-gray-800 transition select-none"
                  >
                    <div className="flex items-center gap-1.5">
                      <span>Farm Name</span>
                      {sortField === 'name' && (
                        <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th className="w-1/4 text-xs font-semibold uppercase tracking-wider text-gray-500 px-6 py-4">
                    Location
                  </th>
                  <th
                    onClick={() => handleSort('status')}
                    className="w-1/6 text-xs font-semibold uppercase tracking-wider text-gray-500 px-6 py-4 cursor-pointer hover:text-gray-800 transition select-none"
                  >
                    <div className="flex items-center gap-1.5">
                      <span>Status</span>
                      {sortField === 'status' && (
                        <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('areaHa')}
                    className="w-1/6 text-xs font-semibold uppercase tracking-wider text-gray-500 px-6 py-4 cursor-pointer hover:text-gray-800 transition select-none"
                  >
                    <div className="flex items-center gap-1.5">
                      <span>Lost (ha)</span>
                      {sortField === 'areaHa' && (
                        <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th className="w-1/6 text-xs font-semibold uppercase tracking-wider text-gray-500 px-6 py-4 text-right">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 font-sans">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-gray-400">
                      <div className="flex items-center justify-center gap-2">
                        <svg className="animate-spin h-5 w-5 text-[#5A6B4A]" viewBox="0 0 24 24" fill="none">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        <span className="text-sm">Loading monitored parcels...</span>
                      </div>
                    </td>
                  </tr>
                ) : filteredFarms.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-gray-500 text-sm">
                      No farms found matching &ldquo;{search}&rdquo;.
                    </td>
                  </tr>
                ) : (
                  filteredFarms.map((farm) => (
                    <tr
                      key={farm.id}
                      onClick={() => handleRowClick(farm)}
                      className="hover:bg-[#F9F9F7] transition-colors duration-150 cursor-pointer group"
                    >
                      {/* Farm Name */}
                      <td className="px-6 py-4 text-sm font-medium text-gray-900 group-hover:text-[#5A6B4A] transition-colors">
                        {farm.name}
                      </td>

                      {/* Location Coordinates */}
                      <td className="px-6 py-4 text-sm font-mono text-gray-500">
                        {farm.lat.toFixed(4)}°, {farm.lng.toFixed(4)}°
                      </td>

                      {/* Status Badge */}
                      <td className="px-6 py-4">
                        {getStatusBadge(farm.status)}
                      </td>

                      {/* Lost (ha) */}
                      <td className="px-6 py-4 text-sm font-medium text-gray-700">
                        {farm.loss}
                      </td>

                      {/* Actions */}
                      <td className="px-6 py-4 text-sm font-medium text-right">
                        <span className="text-[#5A6B4A] group-hover:underline inline-flex items-center gap-1">
                          View →
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
