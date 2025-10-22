import React from "react";
import { Activity, AlertCircle, CheckCircle, Loader2 } from "lucide-react";

const ComponentCard = ({ name, healthData, isLoading }) => {
  // Loading state
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border-2 border-gray-200">
        <div className="flex items-center justify-center h-48">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      </div>
    );
  }

  // Error state
  if (healthData?.error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border-2 border-red-300">
        <div className="flex items-center gap-2 mb-4">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <h3 className="text-lg font-semibold text-gray-800">{name}</h3>
        </div>
        <p className="text-sm text-red-600">{healthData.error}</p>
      </div>
    );
  }

  // Extract data
  const {
    health_index = 0,
    status = "Unknown",
    color = "#6B7280",
    description = "No data",
    metrics = {},
  } = healthData || {};

  // Extract metrics from the nested object
  const {
    oee_score = 0,
    performance_rate = 0,
    quality_rate = 0,
    availability_rate = 0,
  } = metrics;

  // Determine status icon and color
  const getStatusIcon = () => {
    if (health_index >= 80) {
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    } else if (health_index >= 60) {
      return <AlertCircle className="w-5 h-5 text-yellow-500" />;
    } else {
      return <AlertCircle className="w-5 h-5 text-red-500" />;
    }
  };

  // Get background color based on health index
  const getBackgroundColor = () => {
    if (health_index >= 80) return "bg-green-50 border-green-300";
    if (health_index >= 60) return "bg-yellow-50 border-yellow-300";
    return "bg-red-50 border-red-300";
  };

  return (
    <div
      className={`rounded-lg shadow-md p-6 border-2 ${getBackgroundColor()} transition-all hover:shadow-lg hover:scale-105 duration-300`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5" style={{ color }} />
          <h3 className="text-lg font-semibold text-gray-800">{name}</h3>
        </div>
        {getStatusIcon()}
      </div>

      {/* Health Index */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-600">
            Health Index
          </span>
          <span className="text-2xl font-bold" style={{ color }}>
            {health_index.toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="h-3 rounded-full transition-all duration-500"
            style={{
              width: `${health_index}%`,
              backgroundColor: color,
            }}
          />
        </div>
      </div>

      {/* Status */}
      <div className="mb-4 p-3 bg-white rounded-md shadow-sm">
        <p className="text-sm font-semibold text-gray-700">Status: {status}</p>
        <p className="text-xs text-gray-600 mt-1">{description}</p>
      </div>

      {/* OEE Metrics */}
      <div className="grid grid-cols-2 gap-3">
        <MetricItem label="OEE" value={oee_score} color="#3B82F6" />
        <MetricItem
          label="Availability"
          value={availability_rate}
          color="#10B981"
        />
        <MetricItem
          label="Performance"
          value={performance_rate}
          color="#F59E0B"
        />
        <MetricItem label="Quality" value={quality_rate} color="#EF4444" />
      </div>
    </div>
  );
};

// Helper component for metrics
const MetricItem = ({ label, value, color }) => (
  <div className="bg-white p-2 rounded shadow-sm">
    <p className="text-xs text-gray-500 mb-1">{label}</p>
    <div className="flex items-center gap-2">
      <div
        className="w-2 h-2 rounded-full"
        style={{ backgroundColor: color }}
      />
      <p className="text-sm font-semibold text-gray-800">
        {typeof value === "number" ? value.toFixed(1) : 0}%
      </p>
    </div>
  </div>
);

export default ComponentCard;
