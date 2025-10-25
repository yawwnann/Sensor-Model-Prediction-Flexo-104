import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import { TrendingUp, BarChart3 } from "lucide-react";

const OEEChart = ({ componentsData, oeeHistory, timestamps }) => {
  // Safety check - return loading state if data not ready
  if (!componentsData || Object.keys(componentsData).length === 0) {
    return (
      <section className="mb-8">
        <div className="bg-white rounded-xl shadow-md p-6 border border-slate-200">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-blue-100 p-2 rounded-lg">
              <BarChart3 className="w-5 h-5 text-blue-600" />
            </div>
            <h2 className="text-xl font-bold text-slate-900">
              OEE Performance Metrics
            </h2>
          </div>
          <div className="flex items-center justify-center h-64 text-slate-500">
            <p>Loading OEE data...</p>
          </div>
        </div>
      </section>
    );
  }

  // Prepare data for bar chart (OEE components by machine component)
  const barChartData = Object.entries(componentsData)
    .filter(([, data]) => !data.error)
    .map(([name, data]) => {
      const metrics = data.metrics || {};
      return {
        name: name.replace("-", " "),
        Availability: metrics.availability_rate || 0,
        Performance: metrics.performance_rate || 0,
        Quality: metrics.quality_rate || 0,
        OEE: metrics.oee_score || 0,
      };
    });

  // If no bar chart data, show placeholder message instead of empty chart
  const hasBarData = barChartData.length > 0 && barChartData.some(d => d.OEE > 0);

  // Prepare data for line chart (OEE trend over time)
  const lineChartData = (oeeHistory && oeeHistory.length > 0) 
    ? oeeHistory.map((point, index) => ({
        time: `T${index + 1}`,
        timeIndex: index + 1,
        OEE: point.oee || 0,
        Availability: point.availability || 0,
        Performance: point.performance || 0,
        Quality: point.quality || 0,
      }))
    : [];

  // Calculate overall OEE metrics
  const calculateOverallMetric = (metricKey) => {
    const values = Object.values(componentsData)
      .filter((data) => !data.error && data.metrics)
      .map((data) => data.metrics[metricKey] || 0);

    if (values.length === 0) return 0;
    return values.reduce((sum, val) => sum + val, 0) / values.length;
  };

  const overallOEE = calculateOverallMetric("oee_score");
  const overallAvailability = calculateOverallMetric("availability_rate");
  const overallPerformance = calculateOverallMetric("performance_rate");
  const overallQuality = calculateOverallMetric("quality_rate");

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-slate-300 rounded-lg shadow-sm">
          <p className="font-semibold text-slate-800 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value.toFixed(2)}%
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-slate-200">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-blue-100 p-2 rounded-lg">
          <BarChart3 className="w-5 h-5 text-blue-600" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">
          OEE (Overall Equipment Effectiveness)
        </h2>
      </div>

      <div className="space-y-6">
        {/* OEE Component Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <OEECard
            title="Overall OEE"
            value={overallOEE}
            color="bg-blue-50 border-blue-200 text-blue-600"
          />
          <OEECard
            title="Availability"
            value={overallAvailability}
          color="bg-emerald-50 border-emerald-200 text-emerald-600"
        />
        <OEECard
          title="Performance"
          value={overallPerformance}
          color="bg-amber-50 border-amber-200 text-amber-600"
        />
        <OEECard
          title="Quality"
          value={overallQuality}
          color="bg-purple-50 border-purple-200 text-purple-600"
        />
      </div>

      {/* OEE Formula */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-slate-800 mb-2">OEE Formula</h3>
        <p className="text-sm text-slate-700">
          OEE = Availability × Performance × Quality
        </p>
        <p className="text-xs text-slate-600 mt-1">
          Overall OEE: {overallOEE.toFixed(2)}% ={" "}
          {overallAvailability.toFixed(2)}% × {overallPerformance.toFixed(2)}% ×{" "}
          {overallQuality.toFixed(2)}%
        </p>
      </div>

      {/* Bar Chart - OEE Components by Machine Component */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-slate-800">
            OEE Components by Machine Component
          </h3>
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="name"
              angle={-45}
              textAnchor="end"
              height={80}
              style={{ fontSize: "12px" }}
            />
            <YAxis
              label={{
                value: "Percentage (%)",
                angle: -90,
                position: "insideLeft",
              }}
              domain={[0, 100]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="Availability" fill="#10B981" />
            <Bar dataKey="Performance" fill="#F59E0B" />
            <Bar dataKey="Quality" fill="#8B5CF6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Line Chart - OEE Trend */}
      {lineChartData.length > 0 ? (
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-slate-800">
              OEE Trend Over Time (Last {lineChartData.length} Points)
            </h3>
          </div>

          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={lineChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="time"
                label={{
                  value: "Time Point",
                  position: "insideBottom",
                  offset: -5,
                }}
              />
              <YAxis
                label={{
                  value: "Percentage (%)",
                  angle: -90,
                  position: "insideLeft",
                }}
                domain={[0, 100]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                type="monotone"
                dataKey="OEE"
                stroke="#3B82F6"
                strokeWidth={3}
                dot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="Availability"
                stroke="#10B981"
                strokeWidth={2}
                strokeDasharray="5 5"
              />
              <Line
                type="monotone"
                dataKey="Performance"
                stroke="#F59E0B"
                strokeWidth={2}
                strokeDasharray="5 5"
              />
              <Line
                type="monotone"
                dataKey="Quality"
                stroke="#8B5CF6"
                strokeWidth={2}
                strokeDasharray="5 5"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-slate-800">
              OEE Trend Over Time
            </h3>
          </div>
          <div className="flex items-center justify-center h-64 text-slate-500">
            <p>Collecting trend data... Please wait for auto-refresh to populate the chart.</p>
          </div>
        </div>
      )}

      {/* OEE Analysis */}
      <div
        className={`border rounded-lg p-4 ${
          overallOEE >= 85
            ? "bg-emerald-50 border-emerald-200"
            : overallOEE >= 70
            ? "bg-amber-50 border-amber-200"
            : "bg-red-50 border-red-200"
        }`}
      >
        <h3 className="font-semibold text-slate-800 mb-2">
          OEE Analysis & Recommendations
        </h3>
        <p className="text-sm text-slate-700 mb-2">
          Current OEE: <strong>{overallOEE.toFixed(2)}%</strong>
        </p>
        <p className="text-sm text-slate-700">
          {overallOEE >= 85
            ? "Excellent! OEE is above world-class standard (85%). Continue monitoring and maintain current practices."
            : overallOEE >= 70
            ? "Good performance but there is room for improvement. Target is 85% or higher."
            : "OEE is below acceptable levels. Immediate action required to improve efficiency."}
        </p>

        {/* Recommendations based on lowest component */}
        {overallOEE < 85 && (
          <div className="mt-3 pt-3 border-t border-slate-200">
            <p className="text-xs font-semibold text-slate-800 mb-1">
              Focus Areas:
            </p>
            <ul className="text-xs text-slate-700 space-y-1">
              {overallAvailability <
                Math.min(overallPerformance, overallQuality) && (
                <li>
                  •{" "}
                  <strong>
                    Availability ({overallAvailability.toFixed(2)}%)
                  </strong>
                  : Reduce downtime and improve equipment reliability
                </li>
              )}
              {overallPerformance <
                Math.min(overallAvailability, overallQuality) && (
                <li>
                  •{" "}
                  <strong>
                    Performance ({overallPerformance.toFixed(2)}%)
                  </strong>
                  : Optimize cycle times and reduce speed losses
                </li>
              )}
              {overallQuality <
                Math.min(overallAvailability, overallPerformance) && (
                <li>
                  • <strong>Quality ({overallQuality.toFixed(2)}%)</strong>:
                  Minimize defects and rework
                </li>
              )}
            </ul>
          </div>
        )}
      </div>
      </div>
    </div>
  );
};

// OEE Card Component
const OEECard = ({ title, value, color }) => (
  <div className={`${color} border rounded-lg p-4`}>
    <p className="text-sm font-medium mb-1">{title}</p>
    <p className="text-2xl font-bold">{value.toFixed(2)}%</p>
  </div>
);

export default OEEChart;
