import React, { useState } from "react";
import {
  Activity,
  AlertCircle,
  CheckCircle,
  Loader2,
  Zap,
  Clock,
  ChevronDown,
  ChevronUp,
  Info,
  AlertTriangle,
} from "lucide-react";

/**
 * ComponentCard - Display individual component health status
 * 
 * Menampilkan health status per komponen untuk monitoring detail
 * 
 * Note: Walaupun komponen ini menampilkan status per komponen,
 * prediction yang dilakukan oleh ML model adalah untuk KESELURUHAN
 * MESIN C_FL104, bukan per komponen.
 * 
 * Component ini digunakan untuk:
 * - Monitoring detail health per komponen
 * - Identifikasi komponen yang memerlukan perhatian
 * - Breakdown health untuk analisis
 * 
 * Sesuai DOKUMENTASI.md:
 * - Model memprediksi total maintenance duration untuk seluruh mesin
 * - Component breakdown untuk monitoring saja
 */

const ComponentCard = ({ name, healthData, isLoading }) => {
  const [showRecommendations, setShowRecommendations] = useState(false);
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
    description = "No data",
    metrics = {},
    auto_prediction = null,
    recommendations = [],
  } = healthData || {};

  // Check if auto-prediction was triggered
  const isAutoPredicted = auto_prediction?.triggered === true;

  // Extract metrics from the nested object
  const {
    oee_score = 0,
    performance_rate = 0,
    quality_rate = 0,
    availability_rate = 0,
  } = metrics;

  // Determine status based on health index
  const getStatusConfig = () => {
    if (health_index >= 80) {
      return {
        icon: <CheckCircle className="w-5 h-5 text-emerald-600" />,
        borderColor: "border-emerald-200",
        bgColor: "bg-emerald-50",
        barColor: "bg-emerald-600",
        textColor: "text-emerald-700",
      };
    } else if (health_index >= 60) {
      return {
        icon: <AlertCircle className="w-5 h-5 text-amber-600" />,
        borderColor: "border-amber-200",
        bgColor: "bg-amber-50",
        barColor: "bg-amber-600",
        textColor: "text-amber-700",
      };
    } else {
      return {
        icon: <AlertTriangle className="w-5 h-5 text-red-600" />,
        borderColor: "border-red-200",
        bgColor: "bg-red-50",
        barColor: "bg-red-600",
        textColor: "text-red-700",
      };
    }
  };

  const statusConfig = getStatusConfig();

  return (
    <div
      className={`rounded-lg border-2 ${statusConfig.borderColor} ${statusConfig.bgColor} p-5 transition-all hover:shadow-md relative`}
    >
      {/* Auto-Prediction Badge */}
      {isAutoPredicted && (
        <div className="absolute -top-2 -right-2 z-10">
          <div className="bg-orange-500 text-white px-2.5 py-1 rounded-full text-xs font-bold flex items-center gap-1">
            <Zap className="w-3 h-3" />
            AUTO-PREDICTED
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-slate-700" />
          <h3 className="text-lg font-semibold text-slate-800">{name}</h3>
        </div>
        {statusConfig.icon}
      </div>

      {/* Health Index */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-slate-600">
            Health Index
          </span>
          <span className={`text-2xl font-bold ${statusConfig.textColor}`}>
            {health_index.toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
          <div
            className={`h-2.5 rounded-full transition-all duration-500 ${statusConfig.barColor}`}
            style={{ width: `${health_index}%` }}
          />
        </div>
      </div>

      {/* Status */}
      <div className="mb-4 p-3 bg-white rounded-md border border-slate-200">
        <p className="text-sm font-semibold text-slate-700 flex items-center gap-2">
          <Info className="w-4 h-4" />
          Status: {status}
        </p>
        <p className="text-xs text-slate-600 mt-1">{description}</p>
      </div>

      {/* Auto-Prediction Info */}
      {isAutoPredicted && auto_prediction.prediction_result && (
        <div className="mb-4 p-3 bg-orange-50 border border-orange-200 rounded-md">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-orange-600" />
            <p className="text-xs font-bold text-orange-800">
              AUTO-PREDICTION TRIGGERED
            </p>
          </div>
          {auto_prediction.prediction_result.success ? (
            <>
              <div className="flex items-center gap-2 mb-1">
                <Clock className="w-4 h-4 text-orange-600" />
                <p className="text-sm font-bold text-orange-900">
                  {auto_prediction.prediction_result.prediction_formatted}
                </p>
              </div>
              <p className="text-xs text-orange-700">
                Predicted maintenance duration
              </p>
              <div className="mt-2 pt-2 border-t border-orange-200">
                <p className="text-xs text-orange-600">
                  Critical health detected (below{" "}
                  {auto_prediction.trigger_threshold})
                </p>
              </div>
            </>
          ) : (
            <p className="text-xs text-orange-700">
              Prediction triggered but failed:{" "}
              {auto_prediction.prediction_result.message}
            </p>
          )}
        </div>
      )}

      {/* Recommendations Section */}
      {recommendations && recommendations.length > 0 && (
        <div className="mb-4">
          <button
            onClick={() => setShowRecommendations(!showRecommendations)}
            className="w-full p-3 bg-blue-50 border border-blue-200 rounded-md flex items-center justify-between hover:bg-blue-100 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-semibold text-blue-800">
                Recommendations ({recommendations.length})
              </span>
            </div>
            {showRecommendations ? (
              <ChevronUp className="w-4 h-4 text-blue-600" />
            ) : (
              <ChevronDown className="w-4 h-4 text-blue-600" />
            )}
          </button>

          {showRecommendations && (
            <div className="mt-2 p-3 bg-white border border-blue-200 rounded-md space-y-2">
              {recommendations.map((rec, index) => (
                <div
                  key={index}
                  className="flex items-start gap-2 text-xs text-slate-700"
                >
                  <span className="text-blue-600 font-bold mt-0.5">
                    {index + 1}.
                  </span>
                  <span>{rec}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* OEE Metrics */}
      <div className="grid grid-cols-2 gap-2">
        <MetricItem label="OEE" value={oee_score} color="bg-blue-600" />
        <MetricItem
          label="Availability"
          value={availability_rate}
          color="bg-emerald-600"
        />
        <MetricItem
          label="Performance"
          value={performance_rate}
          color="bg-amber-600"
        />
        <MetricItem label="Quality" value={quality_rate} color="bg-red-600" />
      </div>
    </div>
  );
};

// Helper component for metrics
const MetricItem = ({ label, value, color }) => (
  <div className="bg-white p-2 rounded border border-slate-200">
    <p className="text-xs text-slate-600 mb-1">{label}</p>
    <div className="flex items-center gap-2">
      <div className={`w-2 h-2 rounded-full ${color}`} />
      <p className="text-sm font-semibold text-slate-800">
        {typeof value === "number" ? value.toFixed(1) : 0}%
      </p>
    </div>
  </div>
);

export default ComponentCard;
