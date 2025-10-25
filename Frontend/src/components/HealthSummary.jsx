import React from "react";
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  Activity,
  Zap,
} from "lucide-react";

/**
 * HealthSummary Component
 *
 * Menampilkan ringkasan health status semua komponen dalam format yang lebih compact
 * dan informatif. Alternatif untuk grid ComponentCard yang lebih space-efficient.
 */

const HealthSummary = ({ healthData, isLoading, components }) => {
  // Calculate overall statistics
  const calculateStats = () => {
    const validComponents = Object.entries(healthData)
      .filter(([, data]) => !data.error && data.health_index)
      .map(([name, data]) => ({
        name,
        health: data.health_index,
        status: data.status,
        prediction: data.auto_prediction,
      }));

    if (validComponents.length === 0) {
      return {
        overall: 0,
        critical: 0,
        warning: 0,
        optimal: 0,
        predictions: 0,
      };
    }

    const overall =
      validComponents.reduce((sum, comp) => sum + comp.health, 0) /
      validComponents.length;
    const critical = validComponents.filter((comp) => comp.health < 60).length;
    const warning = validComponents.filter(
      (comp) => comp.health >= 60 && comp.health < 80
    ).length;
    const optimal = validComponents.filter((comp) => comp.health >= 80).length;
    const predictions = validComponents.filter(
      (comp) => comp.prediction?.triggered
    ).length;

    return {
      overall,
      critical,
      warning,
      optimal,
      predictions,
      components: validComponents,
    };
  };

  const stats = calculateStats();

  const getOverallStatus = () => {
    if (stats.overall >= 80)
      return { status: "OPTIMAL", color: "emerald", icon: CheckCircle };
    if (stats.overall >= 60)
      return { status: "WARNING", color: "amber", icon: AlertTriangle };
    return { status: "CRITICAL", color: "red", icon: AlertTriangle };
  };

  const overallStatus = getOverallStatus();

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-md border border-slate-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-slate-200 rounded w-1/3"></div>
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-20 bg-slate-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
      {/* Header */}
      <div
        className={`px-6 py-4 ${
          overallStatus.color === "emerald"
            ? "bg-gradient-to-r from-emerald-500 to-emerald-600"
            : overallStatus.color === "amber"
            ? "bg-gradient-to-r from-amber-500 to-amber-600"
            : "bg-gradient-to-r from-red-500 to-red-600"
        }`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-lg backdrop-blur-sm">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold text-lg">
                System Health Overview
              </h3>
              <p className="text-white/80 text-sm">
                Flexo Machine C_FL104 - All Components
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-lg backdrop-blur-sm">
              <overallStatus.icon className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-white">
                {stats.overall.toFixed(1)}%
              </div>
              <div className="text-white/80 text-sm font-medium">
                {overallStatus.status}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-6">
        {/* Optimal Components */}
        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="w-4 h-4 text-emerald-600" />
            <span className="text-sm font-medium text-emerald-900">
              Optimal
            </span>
          </div>
          <div className="text-2xl font-bold text-emerald-700">
            {stats.optimal}
          </div>
          <div className="text-xs text-emerald-600">≥ 80% Health</div>
        </div>

        {/* Warning Components */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span className="text-sm font-medium text-amber-900">Warning</span>
          </div>
          <div className="text-2xl font-bold text-amber-700">
            {stats.warning}
          </div>
          <div className="text-xs text-amber-600">60-79% Health</div>
        </div>

        {/* Critical Components */}
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-red-600" />
            <span className="text-sm font-medium text-red-900">Critical</span>
          </div>
          <div className="text-2xl font-bold text-red-700">
            {stats.critical}
          </div>
          <div className="text-xs text-red-600">&lt; 60% Health</div>
        </div>

        {/* Predictions */}
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-orange-600" />
            <span className="text-sm font-medium text-orange-900">
              Predicted
            </span>
          </div>
          <div className="text-2xl font-bold text-orange-700">
            {stats.predictions}
          </div>
          <div className="text-xs text-orange-600">Auto-triggered</div>
        </div>
      </div>

      {/* Component List */}
      <div className="border-t border-slate-200 bg-slate-50">
        <div className="px-6 py-3">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="w-4 h-4 text-slate-600" />
            <span className="text-sm font-semibold text-slate-700">
              Component Details
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {stats.components.map((component) => (
              <ComponentRow key={component.name} component={component} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Component untuk setiap row komponen
const ComponentRow = ({ component }) => {
  const getHealthColor = (health) => {
    if (health >= 80)
      return "text-emerald-600 bg-emerald-50 border-emerald-200";
    if (health >= 60) return "text-amber-600 bg-amber-50 border-amber-200";
    return "text-red-600 bg-red-50 border-red-200";
  };

  const healthColor = getHealthColor(component.health);

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-3 hover:shadow-sm transition-all">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-slate-700">
          {component.name}
        </span>
        {component.prediction?.triggered && (
          <div className="bg-orange-500 text-white px-2 py-0.5 rounded text-xs font-bold">
            <Zap className="w-3 h-3 inline mr-1" />
            PRED
          </div>
        )}
      </div>

      <div className="flex items-center justify-between">
        <div
          className={`px-2 py-1 rounded-md border text-xs font-bold ${healthColor}`}
        >
          {component.health.toFixed(1)}%
        </div>
        <div className="text-xs text-slate-500">{component.status}</div>
      </div>

      {/* Mini health bar */}
      <div className="w-full bg-slate-200 rounded-full h-1 mt-2">
        <div
          className={`h-1 rounded-full transition-all duration-300 ${
            component.health >= 80
              ? "bg-emerald-500"
              : component.health >= 60
              ? "bg-amber-500"
              : "bg-red-500"
          }`}
          style={{ width: `${component.health}%` }}
        />
      </div>
    </div>
  );
};

export default HealthSummary;
