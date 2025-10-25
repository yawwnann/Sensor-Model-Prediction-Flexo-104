import React, { useState, useEffect } from "react";
import { AlertTriangle, X, Zap, Clock, TrendingDown, Activity } from "lucide-react";
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
    const avgHealth = validComponents.reduce((sum, comp) => sum + comp.health, 0) / validComponents.length;

    // Check if any component has triggered prediction or overall health is critical
    const hasTriggeredPrediction = validComponents.some(
      comp => comp.prediction?.triggered === true
    );

    // Get the most critical component's prediction
    const criticalComponent = validComponents
      .filter(comp => comp.prediction?.triggered === true)
      .sort((a, b) => a.health - b.health)[0];

    if (hasTriggeredPrediction || avgHealth <= 40) {
      // Get prediction formatted string (e.g., "2 jam 30 menit")
      const predictionFormatted = criticalComponent?.prediction?.prediction_result?.prediction_formatted || 
                                  `${Math.ceil((100 - avgHealth) / 10)} jam 0 menit`;
      
      setOverallPrediction({
        overallHealth: avgHealth,
        triggered: true,
        criticalComponents: validComponents.filter(comp => comp.health <= 40),
        predictionFormatted: predictionFormatted,
        componentCount: validComponents.length,
        criticalCount: validComponents.filter(comp => comp.health <= 40).length,
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
    <div className="fixed bottom-4 right-4 z-50 w-[420px] max-h-[80vh] overflow-y-auto">
      <div className="bg-gradient-to-br from-orange-50 to-red-50 border-l-4 border-orange-500 rounded-xl shadow-2xl">
        <div className="p-5">
          {/* Header with dismiss button */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-xl p-2 shadow-lg">
                <AlertTriangle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-orange-500" />
                  Maintenance Alert
                </h3>
                <p className="text-xs text-slate-600 mt-0.5 flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5" />
                  Overall Machine Health Critical
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsDismissed(true)}
              className="text-slate-400 hover:text-slate-600 transition-colors p-1 hover:bg-white/50 rounded"
              aria-label="Dismiss alert"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Overall Health Status */}
          <div className="bg-white rounded-xl p-4 border border-orange-200 shadow-sm mb-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-slate-600">Overall Machine Health</span>
              <div className="flex items-center gap-2">
                <div className={`w-2.5 h-2.5 rounded-full ${
                  overallPrediction.overallHealth >= 60 ? 'bg-yellow-500' :
                  overallPrediction.overallHealth >= 40 ? 'bg-orange-500' : 'bg-red-500'
                } animate-pulse`}></div>
                <span className={`text-2xl font-bold ${
                  overallPrediction.overallHealth >= 60 ? 'text-yellow-600' :
                  overallPrediction.overallHealth >= 40 ? 'text-orange-600' : 'text-red-600'
                }`}>
                  {overallPrediction.overallHealth.toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-slate-200 rounded-full h-2 mb-3">
              <div 
                className={`h-2 rounded-full transition-all duration-500 ${
                  overallPrediction.overallHealth >= 60 ? 'bg-yellow-500' :
                  overallPrediction.overallHealth >= 40 ? 'bg-orange-500' : 'bg-red-500'
                }`}
                style={{ width: `${overallPrediction.overallHealth}%` }}
              ></div>
            </div>

            {/* Critical Components Count */}
            <div className="flex items-center justify-between text-xs text-slate-600">
              <span>{overallPrediction.criticalCount} of {overallPrediction.componentCount} components critical</span>
              <span className="font-semibold text-orange-600">⚠ Health ≤ 40%</span>
            </div>
          </div>

          {/* Maintenance Prediction */}
          <div className="bg-white rounded-xl p-4 border border-orange-200 shadow-sm mb-4">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-4 h-4 text-orange-500" />
              <span className="text-sm font-semibold text-slate-700">Predicted Maintenance Duration:</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-orange-600">
                {overallPrediction.predictionFormatted}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Based on current degradation rate and machine learning model
            </p>
          </div>

          {/* Critical Components List */}
          {overallPrediction.criticalComponents.length > 0 && (
            <div className="bg-white rounded-xl p-4 border border-orange-200 shadow-sm">
              <div className="flex items-center gap-2 mb-3">
                <TrendingDown className="w-4 h-4 text-red-500" />
                <span className="text-sm font-semibold text-slate-700">Critical Components:</span>
              </div>
              <div className="space-y-2">
                {overallPrediction.criticalComponents.map((comp) => (
                  <div key={comp.name} className="flex items-center justify-between p-2 bg-red-50 rounded-lg">
                    <span className="text-xs font-medium text-slate-700">{comp.name}</span>
                    <span className="text-xs font-bold text-red-600">{comp.health.toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Message */}
          <div className="mt-4 p-3 bg-orange-100 rounded-lg border border-orange-200">
            <p className="text-xs text-slate-700 font-medium">
              🔧 <strong>Action Required:</strong> Schedule maintenance to prevent unplanned downtime
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutoPredictionAlert;
