import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp } from "lucide-react";

const TrendChart = ({ healthHistory, timestamps }) => {
  // Prepare data for line chart
  const chartData = timestamps.map((timestamp, index) => {
    const dataPoint = {
      time: timestamp,
      timeLabel: `T-${timestamps.length - index}`,
    };

    // Add each component's health data
    Object.entries(healthHistory).forEach(([component, history]) => {
      if (history[index] !== undefined) {
        dataPoint[component] = history[index];
      }
    });

    return dataPoint;
  });

  // Component colors
  const colors = {
    "Pre-Feeder": "#EF4444",
    Feeder: "#F59E0B",
    Printing: "#10B981",
    Slotter: "#3B82F6",
    Stacker: "#8B5CF6",
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-slate-300 rounded-lg shadow-sm">
          <p className="font-semibold text-slate-800 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value?.toFixed(2)}%
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-slate-800">
          Health Index Trend (Last {chartData.length} Points)
        </h3>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timeLabel"
            label={{
              value: "Time Point",
              position: "insideBottom",
              offset: -5,
            }}
            style={{ fontSize: "12px" }}
          />
          <YAxis
            label={{
              value: "Health Index (%)",
              angle: -90,
              position: "insideLeft",
            }}
            domain={[0, 100]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          {Object.entries(healthHistory).map(([component]) => (
            <Line
              key={component}
              type="monotone"
              dataKey={component}
              stroke={colors[component] || "#6B7280"}
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4">
        {Object.entries(healthHistory).map(([component, history]) => {
          const latestValue = history[history.length - 1] || 0;
          const avgValue =
            history.length > 0
              ? history.reduce((sum, val) => sum + val, 0) / history.length
              : 0;
          const trend =
            history.length >= 2 ? latestValue - history[history.length - 2] : 0;

          return (
            <div
              key={component}
              className="bg-slate-50 rounded-lg p-3 border border-slate-200"
            >
              <p className="text-xs text-slate-600 mb-1">{component}</p>
              <p className="text-lg font-bold text-slate-800">
                {latestValue.toFixed(1)}%
              </p>
              <div className="flex items-center gap-2 mt-1">
                <span
                  className={`text-xs font-semibold ${
                    trend > 0
                      ? "text-emerald-600"
                      : trend < 0
                      ? "text-red-600"
                      : "text-slate-600"
                  }`}
                >
                  {trend > 0 ? "↑" : trend < 0 ? "↓" : "→"}{" "}
                  {Math.abs(trend).toFixed(1)}
                </span>
                <span className="text-xs text-slate-500">
                  Avg: {avgValue.toFixed(1)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TrendChart;
