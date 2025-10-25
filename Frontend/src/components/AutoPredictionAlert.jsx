import React, { useState, useEffect } from "react";
import {
  AlertTriangle,
  X,
  Zap,
  Clock,
  TrendingDown,
  Activity,
} from "lucide-react";
import { useNotification } from "../contexts/NotificationContext";

/**
 * AutoPredictionAlert Component
 *
 * Menampilkan global alert untuk overall machine prediction
 *
 * IMPORTANT: Sesuai DOKUMENTASI.md
 * - Auto-trigger ketika overall machine health < 40%
 * - Prediksi untuk KESELURUHAN MESIN C_FL104
 * - Bukan prediksi per komponen individual
 * - Menampilkan estimasi total maintenance duration untuk seluruh mesin
 * - Dapat di-toggle on/off dari Navbar
 *
 * Alasan prediksi untuk seluruh mesin:
 * 1. Interdependensi komponen
 * 2. Efisiensi operasional (maintenance sekaligus)
 * 3. Data training model mencakup seluruh mesin
 * 4. Business logic industri printing (preventive maintenance komprehensif)
 * 5. Cost effectiveness (mengurangi total downtime)
 */
const AutoPredictionAlert = ({ healthData }) => {
  const [overallPrediction, setOverallPrediction] = useState(null);
  const [isDismissed, setIsDismissed] = useState(false);

  // Get notification settings from context
  const { notificationsEnabled } = useNotification();

  useEffect(() => {
    // Calculate overall machine health and prediction
    // Menghitung health keseluruhan mesin C_FL104
    const validComponents = Object.entries(healthData)
      .filter(([, data]) => !data.error && data.health_index)
      .map(([name, data]) => ({
        name,
        health: data.health_index,
        prediction: data.auto_prediction,
      }));

    if (validComponents.length === 0) {
      setOverallPrediction(null);
      return;
    }

    // Calculate average health
    const avgHealth =
      validComponents.reduce((sum, comp) => sum + comp.health, 0) /
      validComponents.length;

    // Check if any component has triggered prediction or overall health is critical
    const hasTriggeredPrediction = validComponents.some(
      (comp) => comp.prediction?.triggered === true
    );

    // Get the most critical component's prediction
    const criticalComponent = validComponents
      .filter((comp) => comp.prediction?.triggered === true)
      .sort((a, b) => a.health - b.health)[0];

    if (hasTriggeredPrediction || avgHealth <= 40) {
      // Get prediction formatted string (e.g., "2 jam 30 menit")
      const predictionFormatted =
        criticalComponent?.prediction?.prediction_result
          ?.prediction_formatted ||
        `${Math.ceil((100 - avgHealth) / 10)} jam 0 menit`;

      setOverallPrediction({
        overallHealth: avgHealth,
        triggered: true,
        criticalComponents: validComponents.filter((comp) => comp.health <= 40),
        predictionFormatted: predictionFormatted,
        componentCount: validComponents.length,
        criticalCount: validComponents.filter((comp) => comp.health <= 40)
          .length,
      });
      setIsDismissed(false); // Show alert when triggered
    } else {
      setOverallPrediction(null);
    }
  }, [healthData]);

  // Don't show if:
  // 1. Notifications are disabled globally
  // 2. Alert is dismissed by user
  // 3. No prediction triggered
  if (!notificationsEnabled || isDismissed || !overallPrediction) {
    return null;
  }

  return (
    <div className="fixed top-20 right-4 z-50 w-80 animate-slide-in-right">
      <div className="bg-white border border-orange-300 rounded-lg shadow-lg overflow-hidden">
        {/* Compact Header */}
        <div className="bg-gradient-to-r from-orange-500 to-red-500 px-4 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-white" />
              <span className="text-white font-semibold text-sm">
                Maintenance Alert
              </span>
            </div>
            <button
              onClick={() => setIsDismissed(true)}
              className="text-white/80 hover:text-white transition-colors p-1 hover:bg-white/10 rounded"
              aria-label="Dismiss alert"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Compact Content */}
        <div className="p-4">
          {/* Health & Prediction in one row */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div
                className={`w-3 h-3 rounded-full animate-pulse ${
                  overallPrediction.overallHealth >= 60
                    ? "bg-yellow-500"
                    : overallPrediction.overallHealth >= 40
                    ? "bg-orange-500"
                    : "bg-red-500"
                }`}
              ></div>
              <span className="text-xs text-slate-600">Health:</span>
              <span
                className={`text-sm font-bold ${
                  overallPrediction.overallHealth >= 60
                    ? "text-yellow-600"
                    : overallPrediction.overallHealth >= 40
                    ? "text-orange-600"
                    : "text-red-600"
                }`}
              >
                {overallPrediction.overallHealth.toFixed(1)}%
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Clock className="w-3 h-3 text-orange-500" />
              <span className="text-sm font-bold text-orange-600">
                {overallPrediction.predictionFormatted}
              </span>
            </div>
          </div>

          {/* Thin Progress Bar */}
          <div className="w-full bg-slate-200 rounded-full h-1.5 mb-3">
            <div
              className={`h-1.5 rounded-full transition-all duration-500 ${
                overallPrediction.overallHealth >= 60
                  ? "bg-yellow-500"
                  : overallPrediction.overallHealth >= 40
                  ? "bg-orange-500"
                  : "bg-red-500"
              }`}
              style={{ width: `${overallPrediction.overallHealth}%` }}
            ></div>
          </div>

          {/* Critical Components Summary */}
          {overallPrediction.criticalComponents.length > 0 && (
            <div className="text-xs text-slate-600 mb-3">
              <span className="font-medium text-red-600">
                {overallPrediction.criticalCount} kritical:
              </span>{" "}
              {overallPrediction.criticalComponents
                .map((comp) => comp.name)
                .join(", ")}
            </div>
          )}

          {/* Compact Action */}
          <div className="bg-orange-50 border border-orange-200 rounded px-3 py-2">
            <p className="text-xs text-slate-700">
              <span className="font-semibold text-orange-600">⚠ Action:</span>{" "}
              Schedule maintenance to prevent downtime
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutoPredictionAlert;
