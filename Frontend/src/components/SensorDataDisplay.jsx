import { useState, useEffect } from "react";
import {
  Activity,
  Database,
  Cpu,
  Gauge,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Calendar,
  Clock,
} from "lucide-react";

/**
 * SensorDataDisplay - Real-time sensor data display component
 *
 * Menampilkan data sensor secara langsung dari database tanpa analisis downtime.
 * Data diambil dari endpoint /api/sensor/realtime yang mengambil langsung dari machine_logs.
 */

const SensorDataDisplay = ({ limit = 10 }) => {
  const [sensorData, setSensorData] = useState([]);
  const [currentStatus, setCurrentStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Fetch sensor data from API
  const fetchSensorData = async () => {
    try {
      setIsRefreshing(true);
      setError(null);

      // Fetch real-time sensor data
      const response = await fetch(
        `http://localhost:5000/api/sensor/realtime?limit=${limit}`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();

      if (data.success) {
        setSensorData(data.data || []);
        setLastUpdate(new Date());
      } else {
        throw new Error(data.message || "Failed to fetch sensor data");
      }

      // Fetch current status
      const currentResponse = await fetch(
        "http://localhost:5000/api/sensor/current"
      );
      if (currentResponse.ok) {
        const currentData = await currentResponse.json();
        if (currentData.success) {
          setCurrentStatus(currentData.data);
        }
      }

      setIsLoading(false);
    } catch (err) {
      console.error("Error fetching sensor data:", err);
      setError(err.message);
      setIsLoading(false);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Auto-refresh every 5 seconds
  useEffect(() => {
    fetchSensorData();
    const interval = setInterval(fetchSensorData, 5000);
    return () => clearInterval(interval);
  }, [limit]);

  // Manual refresh
  const handleRefresh = () => {
    fetchSensorData();
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString("id-ID", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case "Running":
        return "text-green-600 bg-green-50 border-green-200";
      case "Downtime":
        return "text-red-600 bg-red-50 border-red-200";
      case "Maintenance":
        return "text-blue-600 bg-blue-50 border-blue-200";
      case "Error":
        return "text-red-600 bg-red-50 border-red-200";
      case "Idle":
        return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "Stopped":
        return "text-orange-600 bg-orange-50 border-orange-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  // Get performance color
  const getPerformanceColor = (value) => {
    if (value >= 80) return "text-green-600";
    if (value >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-md border border-slate-200 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-blue-100 p-3 rounded-lg">
            <Database className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">
              Data Sensor Real-time
            </h2>
            <p className="text-sm text-slate-600">Memuat data sensor...</p>
          </div>
        </div>

        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-slate-100 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-md border border-slate-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-red-100 p-3 rounded-lg">
            <Database className="w-6 h-6 text-red-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">
              Data Sensor Real-time
            </h2>
            <p className="text-sm text-red-600">Error: {error}</p>
          </div>
        </div>

        <button
          onClick={handleRefresh}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md border border-slate-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 rounded-t-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/10 p-2 rounded-lg backdrop-blur-sm">
              <Database className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-white font-semibold text-lg">
                Data Sensor Real-time
              </h2>
              <p className="text-blue-100 text-sm">
                Data langsung dari sensor mesin C_FL104
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {lastUpdate && (
              <div className="text-right">
                <p className="text-blue-100 text-xs">Terakhir diperbarui</p>
                <p className="text-white text-sm font-medium">
                  {lastUpdate.toLocaleTimeString("id-ID")}
                </p>
              </div>
            )}

            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-all disabled:opacity-50"
              title="Refresh data"
            >
              <RefreshCw
                className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* Current Status Card */}
      {currentStatus && (
        <div className="p-6 border-b border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Status Terkini
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div
              className={`p-3 rounded-lg border ${getStatusColor(
                currentStatus.machine_status
              )}`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-lg">{currentStatus.status_icon}</span>
                <span className="font-medium text-sm">Status Mesin</span>
              </div>
              <p className="font-bold">{currentStatus.machine_status}</p>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <div className="flex items-center gap-2 mb-1">
                <Gauge className="w-4 h-4 text-slate-600" />
                <span className="font-medium text-sm text-slate-600">
                  Performance
                </span>
              </div>
              <p
                className={`font-bold ${getPerformanceColor(
                  currentStatus.performance_rate
                )}`}
              >
                {currentStatus.performance_rate}%
              </p>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <div className="flex items-center gap-2 mb-1">
                <Cpu className="w-4 h-4 text-slate-600" />
                <span className="font-medium text-sm text-slate-600">
                  Quality
                </span>
              </div>
              <p
                className={`font-bold ${getPerformanceColor(
                  currentStatus.quality_rate
                )}`}
              >
                {currentStatus.quality_rate}%
              </p>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <div className="flex items-center gap-2 mb-1">
                <Clock className="w-4 h-4 text-slate-600" />
                <span className="font-medium text-sm text-slate-600">
                  Availability
                </span>
              </div>
              <p
                className={`font-bold ${getPerformanceColor(
                  currentStatus.availability_rate || 0
                )}`}
              >
                {currentStatus.availability_rate || 0}%
              </p>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="w-4 h-4 text-slate-600" />
                <span className="font-medium text-sm text-slate-600">
                  Total Produksi
                </span>
              </div>
              <p className="font-bold text-slate-900">
                {currentStatus.cumulative_production} pcs
              </p>
              <p className="text-xs text-slate-500">
                Defect: {currentStatus.defect_rate}%
              </p>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <div className="flex items-center gap-2 mb-1">
                <Activity className="w-4 h-4 text-slate-600" />
                <span className="font-medium text-sm text-slate-600">
                  Interval (5s)
                </span>
              </div>
              <p
                className={`font-bold ${
                  currentStatus.interval_production > 0
                    ? "text-green-600"
                    : "text-red-600"
                }`}
              >
                {currentStatus.interval_production || 0} pcs
              </p>
              <p className="text-xs text-slate-500">Saat ini</p>
            </div>
          </div>
        </div>
      )}

      {/* Sensor Data Table */}
      <div className="p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5" />
          Riwayat Data Sensor ({sensorData.length} records)
        </h3>

        {sensorData.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <Database className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Tidak ada data sensor tersedia</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-4 font-semibold text-slate-700">
                    Waktu
                  </th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-700">
                    Status
                  </th>
                  <th className="text-right py-3 px-4 font-semibold text-slate-700">
                    Performance
                  </th>
                  <th className="text-right py-3 px-4 font-semibold text-slate-700">
                    Quality
                  </th>
                  <th className="text-right py-3 px-4 font-semibold text-slate-700">
                    Availability
                  </th>
                  <th className="text-right py-3 px-4 font-semibold text-slate-700">
                    Produksi
                  </th>
                  <th className="text-right py-3 px-4 font-semibold text-slate-700">
                    Defects
                  </th>
                </tr>
              </thead>
              <tbody>
                {sensorData.map((record, index) => (
                  <tr
                    key={record.id}
                    className={`border-b border-slate-100 hover:bg-slate-50 ${
                      index === 0 ? "bg-blue-50/50" : ""
                    }`}
                  >
                    <td className="py-3 px-4 text-slate-600">
                      {formatTimestamp(record.timestamp)}
                      {index === 0 && (
                        <span className="ml-2 text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded-full">
                          Terbaru
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(
                          record.machine_status
                        )}`}
                      >
                        <span>{record.status_icon}</span>
                        {record.machine_status}
                      </span>
                    </td>
                    <td
                      className={`py-3 px-4 text-right font-medium ${getPerformanceColor(
                        record.performance_rate
                      )}`}
                    >
                      {record.performance_rate}%
                    </td>
                    <td
                      className={`py-3 px-4 text-right font-medium ${getPerformanceColor(
                        record.quality_rate
                      )}`}
                    >
                      {record.quality_rate}%
                    </td>
                    <td
                      className={`py-3 px-4 text-right font-medium ${getPerformanceColor(
                        record.availability_rate || 0
                      )}`}
                    >
                      {record.availability_rate || 0}%
                    </td>
                    <td className="py-3 px-4 text-right font-medium text-slate-900">
                      {record.cumulative_production?.toLocaleString()} pcs
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="text-slate-900 font-medium">
                        {record.cumulative_defects?.toLocaleString()} pcs
                      </div>
                      <div
                        className={`text-xs ${getPerformanceColor(
                          100 - record.defect_rate
                        )}`}
                      >
                        ({record.defect_rate}%)
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default SensorDataDisplay;
