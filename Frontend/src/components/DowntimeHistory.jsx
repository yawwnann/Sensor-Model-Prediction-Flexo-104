import React, { useState, useEffect } from "react";
import {
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Calendar,
  TrendingUp,
  Info,
  ChevronDown,
  ChevronUp,
  Filter,
} from "lucide-react";
import { fetchDowntimeHistory, fetchDowntimeStatistics } from "../services/api";

/**
 * DowntimeHistory Component
 *
 * Menampilkan riwayat downtime mesin Flexo C_FL104
 * Data diambil dari backend berdasarkan analisis machine_logs
 *
 * Features:
 * - Historical downtime records from machine_logs
 * - Duration & reason tracking
 * - Component-wise breakdown
 * - Filter by date range & component
 * - Real-time statistics
 *
 * @param {number} limit - Maximum number of records to display
 */

const DowntimeHistory = ({ limit = 50 }) => {
  const [downtimeRecords, setDowntimeRecords] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedRow, setExpandedRow] = useState(null);
  const [filterComponent, setFilterComponent] = useState("all");
  const [dateRange, setDateRange] = useState("7days");
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch downtime data from API
  useEffect(() => {
    fetchDowntimeData();
  }, [dateRange, filterComponent, limit]);

  // Auto-refresh every 5 seconds
  useEffect(() => {
    if (!autoRefresh) return;

    const intervalId = setInterval(() => {
      console.log("🔄 Auto-refreshing downtime data...");
      fetchDowntimeData();
      setLastRefresh(new Date());
    }, 5000); // 5 seconds

    return () => clearInterval(intervalId);
  }, [dateRange, filterComponent, limit, autoRefresh]);

  const fetchDowntimeData = async (silentRefresh = false) => {
    try {
      // Only show loading spinner on initial load, not on auto-refresh
      if (!silentRefresh) {
        setIsLoading(true);
      }
      setError(null);

      // Calculate date filters based on date range
      const { startDate, endDate } = getDateRangeFilter(dateRange);

      // Fetch downtime history
      const historyData = await fetchDowntimeHistory(
        limit,
        filterComponent,
        startDate,
        endDate
      );

      console.log("📡 Raw downtime history from API:", historyData);

      // Fetch statistics
      const statsData = await fetchDowntimeStatistics(startDate, endDate);

      console.log("📊 Raw statistics from API:", statsData);

      // Transform API data to component format
      const transformedRecords = transformDowntimeData(historyData);

      console.log("🔄 Transformed records:", transformedRecords);

      setDowntimeRecords(transformedRecords);
      setStatistics(statsData);
      setIsLoading(false);

      console.log(`✅ Loaded ${transformedRecords.length} downtime records`);

      // Show info if no data found
      if (transformedRecords.length === 0) {
        console.log("ℹ️ No downtime records found. This means:");
        console.log("  - Machine is running smoothly with no downtime events");
        console.log(
          "  - Or sensor_simulator.py needs to be run to generate machine_logs"
        );
        console.log(
          "  - Or the selected filters (date range/component) have no matching data"
        );
      }
    } catch (err) {
      console.error("Error fetching downtime data:", err);
      setError(err.message || "Failed to load downtime data");
      setIsLoading(false);

      // Fallback to empty data
      setDowntimeRecords([]);
      setStatistics(null);
    }
  };

  const getDateRangeFilter = (range) => {
    const now = new Date();
    let startDate = null;
    const endDate = now.toISOString().split("T")[0];

    switch (range) {
      case "7days":
        startDate = new Date(now.setDate(now.getDate() - 7))
          .toISOString()
          .split("T")[0];
        break;
      case "30days":
        startDate = new Date(now.setDate(now.getDate() - 30))
          .toISOString()
          .split("T")[0];
        break;
      case "90days":
        startDate = new Date(now.setDate(now.getDate() - 90))
          .toISOString()
          .split("T")[0];
        break;
      case "all":
      default:
        startDate = null;
        break;
    }

    return { startDate, endDate };
  };

  const transformDowntimeData = (apiData) => {
    if (!apiData || !Array.isArray(apiData)) {
      console.log("⚠️ Invalid API data format:", apiData);
      return [];
    }

    console.log(
      `📊 Transforming ${apiData.length} downtime records from backend`
    );

    return apiData.map((item) => {
      // Calculate duration in human-readable format
      const durationMinutes = item.duration || 0;
      const hours = Math.floor(durationMinutes / 60);
      const minutes = durationMinutes % 60;
      const durationText =
        hours > 0 ? `${hours} jam ${minutes} menit` : `${minutes} menit`;

      // Format timestamp for display
      const displayTimestamp = item.timestamp
        ? new Date(item.timestamp).toLocaleString("id-ID", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
          })
        : "N/A";

      return {
        id: item.id || `downtime-${Date.now()}-${Math.random()}`,
        timestamp: displayTimestamp,
        component: item.component || "Unknown",
        reason: item.reason || "No reason specified",
        duration: durationText,
        durationMinutes: durationMinutes,
        severity: capitalizeFirst(item.severity) || "Unknown",
        resolved: item.status === "resolved" || item.status === "resolved",
        resolvedBy: item.technician || "Auto-detected",
        actions: item.notes ? [item.notes] : ["No additional notes"],
        preventiveMaintenance: item.type === "preventive",
        ongoing: item.ongoing || false,
      };
    });
  };

  const capitalizeFirst = (str) => {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
  };

  // Calculate statistics from data
  const totalDowntime = statistics?.total_duration_minutes || 0;
  const avgDowntime = statistics?.average_duration_minutes || 0;
  const preventiveCount = statistics?.preventive_count || 0;
  const reactiveCount = statistics?.reactive_count || 0;

  // Filter records (additional client-side filtering if needed)
  const filteredRecords = downtimeRecords;

  const toggleRow = (id) => {
    setExpandedRow(expandedRow === id ? null : id);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "High":
      case "Critical":
        return "bg-red-100 text-red-700 border-red-300";
      case "Medium":
        return "bg-amber-100 text-amber-700 border-amber-300";
      case "Low":
        return "bg-blue-100 text-blue-700 border-blue-300";
      case "Scheduled":
        return "bg-green-100 text-green-700 border-green-300";
      default:
        return "bg-gray-100 text-gray-700 border-gray-300";
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case "High":
      case "Critical":
        return <XCircle className="w-4 h-4" />;
      case "Medium":
        return <AlertTriangle className="w-4 h-4" />;
      case "Low":
        return <Info className="w-4 h-4" />;
      case "Scheduled":
        return <CheckCircle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md border border-slate-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 rounded-t-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/10 p-2 rounded-lg backdrop-blur-sm">
              <Clock className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold text-lg">
                Riwayat Downtime
              </h3>
              <p className="text-slate-300 text-sm">
                Mesin Flexo C_FL104 - Last 7 days
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {/* Auto-refresh Toggle */}
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all ${
                autoRefresh
                  ? "bg-green-500/20 text-green-300 border border-green-400/30"
                  : "bg-slate-600/50 text-slate-300 border border-slate-500/30"
              }`}
              title={
                autoRefresh ? "Auto-refresh ON (every 5s)" : "Auto-refresh OFF"
              }
            >
              <div
                className={`w-2 h-2 rounded-full ${
                  autoRefresh ? "bg-green-400 animate-pulse" : "bg-slate-400"
                }`}
              />
              <span className="text-xs font-medium">
                {autoRefresh ? "Live" : "Paused"}
              </span>
            </button>

            {/* Manual Refresh Button */}
            <button
              onClick={() => {
                fetchDowntimeData();
                setLastRefresh(new Date());
              }}
              className="flex items-center gap-2 px-3 py-1.5 bg-blue-500/20 text-blue-300 border border-blue-400/30 rounded-lg hover:bg-blue-500/30 transition-all"
              title="Manual refresh"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </button>

            {/* Records Count */}
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-slate-300" />
              <span className="text-slate-300 text-sm">
                {filteredRecords.length} records
              </span>
            </div>
          </div>
        </div>

        {/* Last Refresh Time */}
        <div className="mt-2 text-xs text-slate-400">
          Last updated: {lastRefresh.toLocaleTimeString()}
        </div>
      </div>

      {/* Statistics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-6 border-b border-slate-200">
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">
              Total Downtime
            </span>
          </div>
          <p className="text-2xl font-bold text-blue-700">
            {Math.floor(totalDowntime / 60)}h {totalDowntime % 60}m
          </p>
        </div>

        <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-purple-600" />
            <span className="text-sm font-medium text-purple-900">
              Avg Duration
            </span>
          </div>
          <p className="text-2xl font-bold text-purple-700">
            {Math.floor(avgDowntime / 60)}h {Math.floor(avgDowntime % 60)}m
          </p>
        </div>

        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span className="text-sm font-medium text-green-900">
              Preventive
            </span>
          </div>
          <p className="text-2xl font-bold text-green-700">{preventiveCount}</p>
        </div>

        <div className="bg-red-50 rounded-lg p-4 border border-red-200">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-red-600" />
            <span className="text-sm font-medium text-red-900">Reactive</span>
          </div>
          <p className="text-2xl font-bold text-red-700">{reactiveCount}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-600" />
            <span className="text-sm font-medium text-slate-700">Filter:</span>
          </div>
          <select
            value={filterComponent}
            onChange={(e) => setFilterComponent(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Components</option>
            <option value="Pre-Feeder">Pre-Feeder</option>
            <option value="Feeder">Feeder</option>
            <option value="Printing">Printing</option>
            <option value="Slotter">Slotter</option>
            <option value="Stacker">Stacker</option>
          </select>

          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="7days">Last 7 Days</option>
            <option value="30days">Last 30 Days</option>
            <option value="90days">Last 90 Days</option>
            <option value="all">All Time</option>
          </select>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading downtime data...</p>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="p-8 text-center">
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 font-medium mb-4">{error}</p>
          <button
            onClick={() => fetchDowntimeData()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && filteredRecords.length === 0 && (
        <div className="p-8 text-center">
          <Clock className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-700 mb-2">
            No Downtime Records Found
          </h3>
          <p className="text-slate-500 mb-4">
            {statistics?.total_downtime === 0
              ? "Machine is running smoothly with no downtime events detected."
              : "No downtime events found for the selected filters."}
          </p>
          <div className="text-sm text-slate-400 space-y-1">
            <p>• Check if the sensor simulator is running to generate data</p>
            <p>• Try adjusting the date range or component filters</p>
            <p>
              • Downtime events are detected from machine_logs when
              performance/quality drops below 20%
            </p>
          </div>
        </div>
      )}

      {/* Downtime Records Table */}
      {!isLoading && !error && filteredRecords.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-100 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Component
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Reason
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Severity
                </th>
                <th className="px-6 py-3 text-center text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Details
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {filteredRecords.map((record) => (
                <React.Fragment key={record.id}>
                  <tr className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                      {record.timestamp}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-lg bg-slate-100 text-slate-700">
                        {record.component}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-700">
                      {record.reason}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-slate-900">
                      {record.duration}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-lg border ${getSeverityColor(
                          record.severity
                        )}`}
                      >
                        {getSeverityIcon(record.severity)}
                        {record.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <button
                        onClick={() => toggleRow(record.id)}
                        className="text-blue-600 hover:text-blue-700 transition-colors"
                      >
                        {expandedRow === record.id ? (
                          <ChevronUp className="w-5 h-5" />
                        ) : (
                          <ChevronDown className="w-5 h-5" />
                        )}
                      </button>
                    </td>
                  </tr>
                  {expandedRow === record.id && (
                    <tr>
                      <td
                        colSpan="6"
                        className="px-6 py-4 bg-blue-50 border-t border-blue-100"
                      >
                        <div className="space-y-3">
                          <div>
                            <h4 className="text-sm font-semibold text-slate-800 mb-2">
                              Actions Taken:
                            </h4>
                            <ul className="list-disc list-inside space-y-1">
                              {record.actions.map((action, idx) => (
                                <li
                                  key={idx}
                                  className="text-sm text-slate-700"
                                >
                                  {action}
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div className="flex items-center gap-4 text-sm">
                            <span className="text-slate-600">
                              <strong>Resolved by:</strong> {record.resolvedBy}
                            </span>
                            {record.preventiveMaintenance && (
                              <span className="px-2 py-1 bg-green-100 text-green-700 rounded-lg text-xs font-medium">
                                Preventive Maintenance
                              </span>
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Footer */}
      <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 rounded-b-xl">
        <p className="text-xs text-slate-600">
          <strong>Note:</strong> Data downtime digunakan untuk analisis
          maintenance predictive dan improvement proses operasional mesin.
        </p>
      </div>
    </div>
  );
};

export default DowntimeHistory;
