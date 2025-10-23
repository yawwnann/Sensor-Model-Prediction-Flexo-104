import React, { useState } from "react";
import { runMaintenancePrediction } from "../services/api";
import { Brain, Loader2, AlertCircle, CheckCircle } from "lucide-react";

const PredictionPanel = () => {
  const [totalProduksi, setTotalProduksi] = useState(10000);
  const [produkCacat, setProdukCacat] = useState(500);
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async () => {
    setIsLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const result = await runMaintenancePrediction({
        total_produksi: parseInt(totalProduksi),
        produk_cacat: parseInt(produkCacat),
      });

      if (result.success) {
        setPrediction(result.data);
      } else {
        setError(result.error);
      }
    } catch {
      setError("Failed to run prediction");
    } finally {
      setIsLoading(false);
    }
  };

  const getPredictionColor = (minutes) => {
    if (minutes < 30) return "text-emerald-600";
    if (minutes < 60) return "text-amber-600";
    return "text-red-600";
  };

  const getPredictionBgColor = (minutes) => {
    if (minutes < 30) return "bg-green-50 border-green-200";
    if (minutes < 60) return "bg-amber-50 border-amber-200";
    return "bg-red-50 border-red-200";
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
      <div className="flex items-center gap-2 mb-4">
        <Brain className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-bold text-slate-800">
          Prediksi Maintenance
        </h2>
      </div>

      <div className="space-y-4">
        {/* Input Total Produksi */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Total Produksi (Pcs)
          </label>
          <input
            type="number"
            value={totalProduksi}
            onChange={(e) => setTotalProduksi(e.target.value)}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            min="0"
            step="100"
          />
        </div>

        {/* Input Produk Cacat */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Produk Cacat (Pcs)
          </label>
          <input
            type="number"
            value={produkCacat}
            onChange={(e) => setProdukCacat(e.target.value)}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            min="0"
            step="10"
          />
        </div>

        {/* Predict Button */}
        <button
          onClick={handlePredict}
          disabled={isLoading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Memproses...
            </>
          ) : (
            <>
              <Brain className="w-5 h-5" />
              Jalankan Prediksi
            </>
          )}
        </button>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-600">Error</p>
              <p className="text-sm text-slate-600">{error}</p>
            </div>
          </div>
        )}

        {/* Prediction Result */}
        {prediction && (
          <div
            className={`border rounded-lg p-4 ${getPredictionBgColor(
              prediction.prediction
            )}`}
          >
            <div className="flex items-start gap-2 mb-3">
              <CheckCircle
                className={`w-5 h-5 shrink-0 mt-0.5 ${getPredictionColor(
                  prediction.prediction
                )}`}
              />
              <div className="flex-1">
                <p className="font-semibold text-slate-800 mb-1">
                  Hasil Prediksi
                </p>
                <p
                  className={`text-2xl font-bold ${getPredictionColor(
                    prediction.prediction
                  )}`}
                >
                  {prediction.prediction_formatted ||
                    `${prediction.prediction.toFixed(2)} menit`}
                </p>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-200">
              <p className="text-xs text-slate-600 font-medium">Input Data:</p>
              <div className="grid grid-cols-2 gap-2 mt-2">
                <div>
                  <p className="text-xs text-slate-500">Total Produksi</p>
                  <p className="text-sm font-semibold text-slate-800">
                    {prediction.input?.total_produksi?.toLocaleString()} pcs
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Produk Cacat</p>
                  <p className="text-sm font-semibold text-slate-800">
                    {prediction.input?.produk_cacat?.toLocaleString()} pcs
                  </p>
                </div>
              </div>
            </div>

            {/* Recommendation */}
            <div className="mt-3 p-3 bg-white rounded border border-slate-200">
              <p className="text-xs font-semibold text-slate-700 mb-1">
                Rekomendasi:
              </p>
              <p className="text-xs text-slate-600">
                {prediction.prediction < 30
                  ? "Kondisi optimal. Lanjutkan monitoring rutin."
                  : prediction.prediction < 60
                  ? "Perhatian diperlukan. Jadwalkan maintenance preventif."
                  : "Tindakan segera diperlukan. Prioritaskan maintenance."}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictionPanel;
