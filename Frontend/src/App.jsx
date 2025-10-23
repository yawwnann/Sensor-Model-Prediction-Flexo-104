import { useState, useEffect } from "react";
import ComponentCard from "./components/ComponentCard";
import PredictionPanel from "./components/PredictionPanel";
import OEEChart from "./components/OEEChart";
import TrendChart from "./components/TrendChart";
import FMEATable from "./components/FMEATable";
import AutoPredictionAlert from "./components/AutoPredictionAlert";
import { fetchAllComponentsHealth } from "./services/api";
import {
  RefreshCw,
  AlertTriangle,
  Activity,
  Settings,
  CheckCircle2,
  AlertCircle,
  BarChart3,
  Search,
} from "lucide-react";
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
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="bg-slate-800 p-2.5 rounded-lg">
                <Settings className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-semibold text-slate-900">
                  FlexoTwin Smart Maintenance
                </h1>
                <p className="text-sm text-slate-600 mt-0.5">
                  Real-Time Machine Health Monitoring System
                </p>
              </div>
            </div>

            {/* Overall Health Badge */}
            <div className="flex items-center gap-3">
              <div className="bg-slate-100 rounded-lg px-5 py-3 border border-slate-200">
                <p className="text-xs text-slate-600 font-medium mb-1">
                  Overall Health
                </p>
                <p className="text-2xl font-bold text-slate-900">
                  {overallHealth.toFixed(1)}%
                </p>
              </div>

              <button
                onClick={handleManualRefresh}
                disabled={isRefreshing}
                className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2.5 rounded-lg flex items-center gap-2 transition-all disabled:opacity-50"
              >
                <RefreshCw
                  className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`}
                />
                <span className="font-medium">Refresh</span>
              </button>
            </div>
          </div>

          {/* Last Update Info */}
          {lastUpdate && (
            <div className="mt-3 flex items-center gap-2 text-sm text-slate-600">
              <Activity className="w-4 h-4" />
              <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
              <span className="mx-2">|</span>
              <span>Auto-refresh every {REFRESH_INTERVAL / 1000}s</span>
            </div>
          )}
        </div>
      </header>

      {/* Auto-Prediction Alert - Global Notification */}
      <AutoPredictionAlert healthData={healthData} />

      {/* Error Banner */}
      {error && (
        <div className="container mx-auto px-6 py-4">
          <div className="bg-red-50 border border-red-200 p-4 rounded-lg flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900 mb-1">
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
      <main className="container mx-auto px-6 py-8">
        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <InfoCard
            title="Total Components"
            value={COMPONENTS.length}
            icon={<Settings className="w-8 h-8" />}
            gradient="from-blue-500 to-blue-600"
          />
          <InfoCard
            title="Healthy Components"
            value={
              Object.values(healthData).filter(
                (d) => !d.error && d.health_index >= 80
              ).length
            }
            icon={<CheckCircle2 className="w-8 h-8" />}
            gradient="from-emerald-500 to-emerald-600"
          />
          <InfoCard
            title="Need Attention"
            value={
              Object.values(healthData).filter(
                (d) => !d.error && d.health_index < 80
              ).length
            }
            icon={<AlertCircle className="w-8 h-8" />}
            gradient="from-amber-500 to-amber-600"
          />
          <InfoCard
            title="Overall Health"
            value={`${overallHealth.toFixed(1)}%`}
            icon={<BarChart3 className="w-8 h-8" />}
            gradient="from-slate-600 to-slate-800"
          />
        </div>

        {/* Section 1: Component Health Cards */}
        <section className="mb-8">
          <div className="flex items-center gap-2 mb-5">
            <Activity className="w-6 h-6 text-slate-700" />
            <h2 className="text-xl font-semibold text-slate-900">
              Component Health Status
            </h2>
          </div>

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
          <div className="flex items-center gap-2 mb-5">
            <BarChart3 className="w-6 h-6 text-slate-700" />
            <h2 className="text-xl font-semibold text-slate-900">
              OEE (Overall Equipment Effectiveness)
            </h2>
          </div>
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
          <div className="flex items-center gap-2 mb-5">
            <Search className="w-6 h-6 text-slate-700" />
            <h2 className="text-xl font-semibold text-slate-900">
              FMEA Analysis
            </h2>
          </div>
          <FMEATable components={COMPONENTS} />
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-12 py-6">
        <div className="container mx-auto px-6 text-center text-slate-600">
          <p className="font-medium">
            FlexoTwin Smart Maintenance 4.0 - Digital Twin Monitoring System
          </p>
          <p className="text-sm mt-1 text-slate-500">
            Backend API: http://localhost:5000 | Frontend: React + Vite
          </p>
        </div>
      </footer>
    </div>
  );
}

// Info Card Component
const InfoCard = ({ title, value, icon, gradient }) => {
  // Convert gradient to solid color mapping
  const colorMap = {
    "from-blue-500 to-blue-600": "bg-blue-600",
    "from-emerald-500 to-emerald-600": "bg-emerald-600",
    "from-amber-500 to-amber-600": "bg-amber-600",
    "from-slate-600 to-slate-800": "bg-slate-700",
  };

  const solidColor = colorMap[gradient] || "bg-slate-700";

  return (
    <div className="bg-white rounded-lg p-5 border border-slate-200 hover:shadow-sm transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-600 mb-2">{title}</p>
          <p className="text-3xl font-bold text-slate-900">{value}</p>
        </div>
        <div className={`${solidColor} p-3 rounded-lg text-white`}>{icon}</div>
      </div>
    </div>
  );
};

export default App;
