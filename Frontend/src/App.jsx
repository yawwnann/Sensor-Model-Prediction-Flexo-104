import { useState, useEffect } from "react";
import ComponentCard from "./components/ComponentCard";
import PredictionPanel from "./components/PredictionPanel";
import OEEChart from "./components/OEEChart";
import TrendChart from "./components/TrendChart";
import FMEATable from "./components/FMEATable";
import { fetchAllComponentsHealth } from "./services/api";
import { RefreshCw, AlertTriangle, Activity } from "lucide-react";
import "./App.css";

// List of machine components
const COMPONENTS = ["Pre-Feeder", "Feeder", "Printing", "Slotter", "Stacker"];

const REFRESH_INTERVAL = 5000; // 5 seconds

function App() {
  const [healthData, setHealthData] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Historical data for trends
  const [healthHistory, setHealthHistory] = useState({
    "Pre-Feeder": [],
    Feeder: [],
    Printing: [],
    Slotter: [],
    Stacker: [],
  });
  const [oeeHistory, setOeeHistory] = useState([]);
  const [timestamps, setTimestamps] = useState([]);

  // Fetch health data for all components
  const fetchData = async () => {
    try {
      setIsRefreshing(true);
      setError(null);

      const data = await fetchAllComponentsHealth(COMPONENTS);
      setHealthData(data);
      setLastUpdate(new Date());

      // Update health history for each component
      const newHealthHistory = { ...healthHistory };
      const newOeeData = [];

      COMPONENTS.forEach((component) => {
        if (data[component] && !data[component].error) {
          const health = data[component].health_index || 0;
          newHealthHistory[component] = [
            ...(healthHistory[component] || []),
            health,
          ].slice(-50); // Keep last 50 points

          // Collect OEE data from metrics object
          const metrics = data[component].metrics || {};
          newOeeData.push({
            oee: metrics.oee_score || 0,
            availability: metrics.availability_rate || 0,
            performance: metrics.performance_rate || 0,
            quality: metrics.quality_rate || 0,
          });
        }
      });

      setHealthHistory(newHealthHistory);

      // Calculate average OEE and add to history
      if (newOeeData.length > 0) {
        const avgOEE = {
          oee:
            newOeeData.reduce((sum, d) => sum + d.oee, 0) / newOeeData.length,
          availability:
            newOeeData.reduce((sum, d) => sum + d.availability, 0) /
            newOeeData.length,
          performance:
            newOeeData.reduce((sum, d) => sum + d.performance, 0) /
            newOeeData.length,
          quality:
            newOeeData.reduce((sum, d) => sum + d.quality, 0) /
            newOeeData.length,
        };
        setOeeHistory((prev) => [...prev, avgOEE].slice(-50)); // Keep last 50 points
      }

      // Add timestamp
      setTimestamps((prev) =>
        [...prev, new Date().toLocaleTimeString()].slice(-50)
      );

      setIsLoading(false);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError(
        "Failed to connect to backend. Please ensure the Flask server is running on http://localhost:5000"
      );
      setIsLoading(false);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Initial fetch and setup interval
  useEffect(() => {
    fetchData();

    const interval = setInterval(() => {
      fetchData();
    }, REFRESH_INTERVAL);

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Manual refresh handler
  const handleManualRefresh = () => {
    fetchData();
  };

  // Calculate overall health
  const calculateOverallHealth = () => {
    const healthValues = Object.values(healthData)
      .filter((data) => !data.error && data.health_index)
      .map((data) => data.health_index);

    if (healthValues.length === 0) return 0;

    return (
      healthValues.reduce((sum, val) => sum + val, 0) / healthValues.length
    );
  };

  const overallHealth = calculateOverallHealth();

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-md border-b-4 border-indigo-500">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
                ⚙️ FlexoTwin Smart Maintenance 4.0
              </h1>
              <p className="text-gray-600 mt-1">
                Real-Time Machine Health Monitoring
              </p>
            </div>

            {/* Overall Health Badge */}
            <div className="flex items-center gap-4">
              <div className="bg-indigo-100 rounded-lg px-4 py-2 border-2 border-indigo-300">
                <p className="text-xs text-indigo-600 font-medium mb-1">
                  Overall Health
                </p>
                <p className="text-2xl font-bold text-indigo-800">
                  {overallHealth.toFixed(1)}%
                </p>
              </div>

              <button
                onClick={handleManualRefresh}
                disabled={isRefreshing}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50"
              >
                <RefreshCw
                  className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`}
                />
                Refresh
              </button>
            </div>
          </div>

          {/* Last Update Info */}
          {lastUpdate && (
            <div className="mt-3 flex items-center gap-2 text-sm text-gray-600">
              <Activity className="w-4 h-4" />
              <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
              <span className="mx-2">•</span>
              <span>Auto-refresh every {REFRESH_INTERVAL / 1000}s</span>
            </div>
          )}
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="container mx-auto px-4 py-4">
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg flex items-start gap-3">
            <AlertTriangle className="w-6 h-6 text-red-600 shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-800 mb-1">
                Connection Error
              </h3>
              <p className="text-red-700 text-sm">{error}</p>
              <p className="text-red-600 text-xs mt-2">
                Make sure the Flask backend is running at http://localhost:5000
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <InfoCard
            title="Total Components"
            value={COMPONENTS.length}
            icon="⚙️"
            color="bg-blue-50 border-blue-300 text-blue-800"
          />
          <InfoCard
            title="Healthy Components"
            value={
              Object.values(healthData).filter(
                (d) => !d.error && d.health_index >= 80
              ).length
            }
            icon="✅"
            color="bg-green-50 border-green-300 text-green-800"
          />
          <InfoCard
            title="Need Attention"
            value={
              Object.values(healthData).filter(
                (d) => !d.error && d.health_index < 80
              ).length
            }
            icon="⚠️"
            color="bg-yellow-50 border-yellow-300 text-yellow-800"
          />
          <InfoCard
            title="Overall Health"
            value={`${overallHealth.toFixed(1)}%`}
            icon="📊"
            color="bg-indigo-50 border-indigo-300 text-indigo-800"
          />
        </div>

        {/* Section 1: Component Health Cards */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Activity className="w-6 h-6 text-indigo-600" />
            Component Health Status
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {COMPONENTS.map((component) => (
              <ComponentCard
                key={component}
                name={component}
                healthData={healthData[component]}
                isLoading={isLoading}
              />
            ))}
          </div>
        </section>

        {/* Section 2: OEE Analysis */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            📊 OEE (Overall Equipment Effectiveness)
          </h2>
          <OEEChart componentsData={healthData} oeeHistory={oeeHistory} />
        </section>

        {/* Section 3: Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Trend Chart - 2 columns */}
          <div className="lg:col-span-2">
            <TrendChart healthHistory={healthHistory} timestamps={timestamps} />
          </div>

          {/* Prediction Panel - 1 column */}
          <div className="lg:col-span-1">
            <PredictionPanel />
          </div>
        </div>

        {/* Section 4: FMEA Analysis */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            🔍 FMEA Analysis
          </h2>
          <FMEATable components={COMPONENTS} />
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t-2 border-gray-200 mt-12 py-6">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>
            FlexoTwin Smart Maintenance 4.0 - Digital Twin Monitoring System
          </p>
          <p className="text-sm mt-1">
            Backend API: http://localhost:5000 | Frontend: React + Vite
          </p>
        </div>
      </footer>
    </div>
  );
}

// Info Card Component
const InfoCard = ({ title, value, icon, color }) => (
  <div className={`${color} border-2 rounded-lg p-4 shadow-md`}>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium opacity-80 mb-1">{title}</p>
        <p className="text-3xl font-bold">{value}</p>
      </div>
      <span className="text-4xl">{icon}</span>
    </div>
  </div>
);

export default App;
