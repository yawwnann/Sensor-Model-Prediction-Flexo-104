import React, { useState, useEffect } from "react";
import { AlertTriangle, X, Zap, Clock, TrendingDown } from "lucide-react";

/**
 * AutoPredictionAlert Component
 * Displays a global alert banner when auto-prediction is triggered on any component
 */
const AutoPredictionAlert = ({ healthData }) => {
  const [autoPredictedComponents, setAutoPredictedComponents] = useState([]);
  const [isDismissed, setIsDismissed] = useState(false);
  const [lastAlertTime, setLastAlertTime] = useState(null);

  useEffect(() => {
    // Find all components with auto-prediction triggered
    const components = Object.entries(healthData)
      .filter(([, data]) => data?.auto_prediction?.triggered === true)
      .map(([name, data]) => ({
        name,
        healthIndex: data.health_index,
        threshold: data.auto_prediction.trigger_threshold,
        predictionResult: data.auto_prediction.prediction_result,
      }));

    setAutoPredictedComponents(components);

    // Reset dismissed state if new predictions appear
    if (components.length > 0 && !isDismissed) {
      setLastAlertTime(new Date());
    }

    // Auto-dismiss after new components are added
    if (components.length > 0) {
      setIsDismissed(false);
    }
  }, [healthData, isDismissed]);

  // Don't show if dismissed or no auto-predictions
  if (isDismissed || autoPredictedComponents.length === 0) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-96 max-h-[80vh] overflow-y-auto">
      <div className="bg-orange-50 border-l-4 border-orange-500 rounded-lg shadow-lg">
        <div className="p-4">
          {/* Header with dismiss button */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="bg-orange-500 rounded-lg p-1.5">
                <AlertTriangle className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-800 flex items-center gap-1.5">
                  <Zap className="w-4 h-4 text-orange-500" />
                  Auto-Prediction Alert
                </h3>
                <p className="text-xs text-slate-600 mt-0.5">
                  {autoPredictedComponents.length} component(s) critical
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsDismissed(true)}
              className="text-slate-500 hover:text-slate-700 transition-colors p-0.5"
              aria-label="Dismiss alert"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Component Cards */}
          <div className="space-y-2">
            {autoPredictedComponents.map((component) => (
              <div
                key={component.name}
                className="bg-white rounded-lg p-3 border border-orange-200"
              >
                {/* Component Name and Health */}
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-bold text-slate-800">
                    {component.name}
                  </h4>
                  <div className="flex items-center gap-1.5 bg-red-50 px-2 py-0.5 rounded border border-red-200">
                    <TrendingDown className="w-3 h-3 text-red-600" />
                    <span className="text-xs font-semibold text-red-600">
                      {component.healthIndex.toFixed(1)}%
                    </span>
                  </div>
                </div>

                {/* Prediction Result */}
                {component.predictionResult?.success ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-4 h-4 text-orange-500" />
                      <p className="text-xs font-semibold text-slate-700">
                        Predicted Duration:
                      </p>
                    </div>
                    <p className="text-lg font-bold text-orange-500 ml-5">
                      {component.predictionResult.prediction_formatted}
                    </p>

                    <div className="space-y-1 text-xs mt-2">
                      <div className="flex justify-between">
                        <span className="text-slate-600">Threshold:</span>
                        <span className="font-semibold text-slate-800">
                          {"<"} {component.threshold}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Input:</span>
                        <span className="font-semibold text-slate-800">
                          {component.predictionResult.input?.total_produksi} pcs
                          / {component.predictionResult.input?.produk_cacat} def
                        </span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-xs text-red-600 bg-red-50 p-2 rounded border border-red-200 flex items-start gap-1.5">
                    <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" />
                    <span>
                      Failed: {component.predictionResult?.message || "Unknown"}
                    </span>
                  </div>
                )}

                {/* Action Recommendation */}
                <div className="mt-2 pt-2 border-t border-slate-200">
                  <div className="flex items-start gap-1.5">
                    <AlertTriangle className="w-3 h-3 text-orange-500 shrink-0 mt-0.5" />
                    <p className="text-xs text-slate-600">
                      Schedule immediate maintenance to prevent breakdown
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Timestamp */}
          {lastAlertTime && (
            <div className="mt-2 text-xs text-slate-500 text-right">
              {lastAlertTime.toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AutoPredictionAlert;
