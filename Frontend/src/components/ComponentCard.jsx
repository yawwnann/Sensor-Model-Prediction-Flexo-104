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
    <div className="bg-white rounded-xl shadow-lg border border-slate-200 hover:shadow-xl transition-all duration-300 relative overflow-hidden">
      {/* Header with status indicator */}
      <div className={`p-4 border-b border-slate-100 ${statusConfig.bgColor}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={`p-2.5 rounded-lg border-2 ${statusConfig.borderColor} bg-white`}
            >
              <Activity className="w-5 h-5 text-slate-700" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-800">{name}</h3>
              <p className="text-xs text-slate-500 font-medium">
                Component Status
              </p>
            </div>
          </div>

          {/* Status Badge */}
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full border-2 ${statusConfig.borderColor} bg-white`}
          >
            {statusConfig.icon}
            <span className={`text-sm font-bold ${statusConfig.textColor}`}>
              {health_index >= 80
                ? "OPTIMAL"
                : health_index >= 60
                ? "WARNING"
                : "CRITICAL"}
            </span>
          </div>
        </div>

        {/* Auto-Prediction Badge */}
        {isAutoPredicted && (
          <div className="absolute top-2 right-2">
            <div className="bg-orange-500 text-white px-2 py-1 rounded-md text-xs font-bold flex items-center gap-1 shadow-lg">
              <Zap className="w-3 h-3" />
              PREDICTED
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="p-4 space-y-4">
        {/* Health Index - Large Display */}
        <div className="text-center">
          <div className={`text-4xl font-bold mb-2 ${statusConfig.textColor}`}>
            {health_index.toFixed(1)}%
          </div>
          <div className="relative w-full bg-slate-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-3 rounded-full transition-all duration-700 ease-out ${statusConfig.barColor}`}
              style={{ width: `${health_index}%` }}
            />
            {/* Health threshold markers */}
            <div className="absolute top-0 left-[60%] w-0.5 h-3 bg-white/50"></div>
            <div className="absolute top-0 left-[80%] w-0.5 h-3 bg-white/50"></div>
          </div>
          <div className="flex justify-between text-xs text-slate-400 mt-1">
            <span>0%</span>
            <span>60%</span>
            <span>80%</span>
            <span>100%</span>
          </div>
        </div>

        {/* Status Description */}
        <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
          <div className="flex items-start gap-2">
            <Info className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-slate-700">{status}</p>
              <p className="text-xs text-slate-600 mt-1">{description}</p>
            </div>
          </div>
        </div>

        {/* Auto-Prediction Section */}
        {isAutoPredicted && auto_prediction.prediction_result && (
          <div className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className="bg-orange-500 p-1.5 rounded-md">
                <Zap className="w-3 h-3 text-white" />
              </div>
              <span className="text-sm font-bold text-orange-800">
                AUTO-PREDICTION
              </span>
            </div>

            {auto_prediction.prediction_result.success ? (
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="w-4 h-4 text-orange-600" />
                  <span className="text-lg font-bold text-orange-900">
                    {auto_prediction.prediction_result.prediction_formatted}
                  </span>
                </div>
                <p className="text-xs text-orange-700">
                  Estimated maintenance duration
                </p>
              </div>
            ) : (
              <p className="text-xs text-orange-700">
                Prediction failed: {auto_prediction.prediction_result.message}
              </p>
            )}
          </div>
        )}

        {/* Recommendations Section */}
        {recommendations && recommendations.length > 0 && (
          <div>
            <button
              onClick={() => setShowRecommendations(!showRecommendations)}
              className="w-full bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg p-3 flex items-center justify-between transition-colors"
            >
              <div className="flex items-center gap-2">
                <div className="bg-blue-500 p-1.5 rounded-md">
                  <Info className="w-3 h-3 text-white" />
                </div>
                <span className="text-sm font-semibold text-blue-800">
                  View Recommendations ({recommendations.length})
                </span>
              </div>
              {showRecommendations ? (
                <ChevronUp className="w-4 h-4 text-blue-600" />
              ) : (
                <ChevronDown className="w-4 h-4 text-blue-600" />
              )}
            </button>

            {showRecommendations && (
              <div className="mt-2 bg-white border border-blue-200 rounded-lg p-3 space-y-2">
                {recommendations.map((rec, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-2 text-sm text-slate-700"
                  >
                    <span className="bg-blue-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center flex-shrink-0 mt-0.5">
                      {index + 1}
                    </span>
                    <span>{rec}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Helper component for metrics
const MetricCard = ({ label, value, color }) => (
  <div className="bg-white border border-slate-200 rounded-lg p-3 hover:shadow-sm transition-shadow">
    <div className="flex items-center gap-2 mb-1">
      <div className={`w-3 h-3 rounded-full ${color}`} />
      <span className="text-xs font-medium text-slate-600">{label}</span>
    </div>
    <div className="text-lg font-bold text-slate-800">
      {typeof value === "number" ? value.toFixed(1) : 0}%
    </div>
    {/* Mini progress bar */}
    <div className="w-full bg-slate-200 rounded-full h-1 mt-1">
      <div
        className={`h-1 rounded-full transition-all duration-300 ${color}`}
        style={{ width: `${typeof value === "number" ? value : 0}%` }}
      />
    </div>
  </div>
);

export default ComponentCard;
