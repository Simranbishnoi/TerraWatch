import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { getReports, downloadReport } from '../api/client';
import Navbar from '../components/Navbar';

export default function Reports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloadingId, setDownloadingId] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadReports() {
      try {
        const data = await getReports();
        if (isMounted && data) {
          setReports(data);
        }
      } catch (err) {
        toast.error('Failed to load reports');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadReports();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleDownload = async (reportId) => {
    setDownloadingId(reportId);
    try {
      if (downloadReport) {
        await downloadReport(reportId);
      }
      toast.success('Report downloaded');
    } catch (err) {
      toast.error('Failed to download report');
    } finally {
      setDownloadingId(null);
    }
  };

  const getRiskBadge = (status) => {
    switch (status) {
      case 'HIGH':
        return (
          <span className="bg-red-50 text-red-700 border border-red-100 px-2 py-0.5 rounded-full text-xs font-medium">
            HIGH
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="bg-amber-50 text-amber-700 border border-amber-100 px-2 py-0.5 rounded-full text-xs font-medium">
            MEDIUM
          </span>
        );
      case 'OK':
      default:
        return (
          <span className="bg-green-50 text-green-700 border border-green-100 px-2 py-0.5 rounded-full text-xs font-medium">
            OK
          </span>
        );
    }
  };

  return (
    <div className="min-h-screen bg-[#F9F9F7] text-[#1A1A1A] font-sans selection:bg-[#5A6B4A]/20 flex flex-col">
      {/* Top Navbar */}
      <Navbar activePage="reports" />

      {/* Main Content Area */}
      <main className="max-w-6xl w-full mx-auto px-6 sm:px-8 py-12 flex-1">
        {/* Header Section */}
        <div className="mb-8">
          <h1 className="font-serif text-4xl text-gray-900 font-medium tracking-tight">
            Generated Reports
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            Download compliance evidence for your monitored farms
          </p>
        </div>

        {/* Reports Grid */}
        {loading ? (
          <div className="py-20 flex items-center justify-center gap-2 text-gray-400">
            <svg
              className="animate-spin h-5 w-5 text-[#5A6B4A]"
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
            <span className="text-sm">Loading compliance dossiers...</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {reports.map((report) => {
              const isDownloading = downloadingId === report.id;
              return (
                <div
                  key={report.id}
                  className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow duration-200 flex flex-col justify-between"
                >
                  <div>
                    {/* Top row */}
                    <div className="flex justify-between items-start mb-4">
                      <span className="text-xs font-mono text-gray-400">
                        {report.id}
                      </span>
                      {getRiskBadge(report.status)}
                    </div>

                    {/* Farm Name */}
                    <h2 className="font-serif text-xl text-gray-900 mb-1 font-medium tracking-tight">
                      {report.farmName}
                    </h2>

                    {/* Date & File Size */}
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-6">
                      <span>{report.date}</span>
                      {report.fileSize && (
                        <>
                          <span>•</span>
                          <span className="font-mono text-gray-400">{report.fileSize}</span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Download Button */}
                  <button
                    onClick={() => handleDownload(report.id)}
                    disabled={isDownloading}
                    className="w-full bg-[#F9F9F7] border border-gray-200 text-gray-700 py-2.5 rounded-full text-sm font-medium hover:bg-[#5A6B4A] hover:text-white hover:border-[#5A6B4A] transition-all duration-200 flex items-center justify-center gap-1.5 shadow-xs disabled:opacity-50 active:scale-95"
                  >
                    {isDownloading ? (
                      <>
                        <svg
                          className="animate-spin h-4 w-4"
                          viewBox="0 0 24 24"
                          fill="none"
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
                        <span>Downloading...</span>
                      </>
                    ) : (
                      <span>Download PDF ↓</span>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
