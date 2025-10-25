import React, { useState } from "react";
import { AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";

/**
 * FMEATable Component
 * 
 * Failure Mode and Effects Analysis (FMEA) Table
 * 
 * Menampilkan analisis FMEA per komponen untuk:
 * - Identifikasi failure modes
 * - Risk assessment (RPN = Severity × Occurrence × Detection)
 * - Recommended actions
 * 
 * Note: FMEA digunakan untuk analisis risiko per komponen,
 * namun maintenance prediction tetap untuk KESELURUHAN MESIN C_FL104
 * 
 * Data FMEA static berdasarkan expert knowledge dan historical data
 */

// FMEA Static Data - Based on historical failures and expert analysis
// Data ini berdasarkan analisis historis mesin Flexo C_FL104
const FMEA_DATA = {
  "Pre-Feeder": {
    rpn: 280,
    failures: [
      {
        mode: "Paper Jam",
        cause: "Roller kotor/aus",
        effect: "Produksi terhenti",
        severity: 8,
        occurrence: 7,
        detection: 5,
      },
      {
        mode: "Feeding Error",
        cause: "Sensor misalignment",
        effect: "Kualitas print buruk",
        severity: 7,
        occurrence: 6,
        detection: 6,
      },
    ],
  },
  Feeder: {
    rpn: 252,
    failures: [
      {
        mode: "Double Feed",
        cause: "Tekanan suction lemah",
        effect: "Material waste",
        severity: 7,
        occurrence: 6,
        detection: 6,
      },
      {
        mode: "Skewed Feed",
        cause: "Guide tidak sejajar",
        effect: "Registrasi tidak akurat",
        severity: 8,
        occurrence: 5,
        detection: 7,
      },
    ],
  },
  Printing: {
    rpn: 320,
    failures: [
      {
        mode: "Ink Smudging",
        cause: "Anilox roller aus",
        effect: "Kualitas print rendah",
        severity: 9,
        occurrence: 6,
        detection: 6,
      },
      {
        mode: "Registration Error",
        cause: "Sensor tidak kalibrasi",
        effect: "Print tidak tepat",
        severity: 8,
        occurrence: 7,
        detection: 6,
      },
    ],
  },
  Slotter: {
    rpn: 210,
    failures: [
      {
        mode: "Blade Tumpul",
        cause: "Wear and tear normal",
        effect: "Slot tidak rapi",
        severity: 7,
        occurrence: 6,
        detection: 5,
      },
      {
        mode: "Misalignment",
        cause: "Getaran berlebih",
        effect: "Dimensi tidak akurat",
        severity: 8,
        occurrence: 5,
        detection: 6,
      },
    ],
  },
  Stacker: {
    rpn: 180,
    failures: [
      {
        mode: "Stack Collapse",
        cause: "Kecepatan terlalu tinggi",
        effect: "Produk rusak",
        severity: 6,
        occurrence: 5,
        detection: 6,
      },
      {
        mode: "Counting Error",
        cause: "Sensor kotor",
        effect: "Salah hitung output",
        severity: 5,
        occurrence: 6,
        detection: 6,
      },
    ],
  },
};

const FMEATable = ({ components }) => {
  // Safety check for components
  const safeComponents = components && components.length > 0 ? components : ["Pre-Feeder", "Feeder", "Printing", "Slotter", "Stacker"];
  
  const [selectedComponent, setSelectedComponent] = useState(
    safeComponents[0] || "Pre-Feeder"
  );
  const [expandedRows, setExpandedRows] = useState([]);

  const toggleRow = (index) => {
    if (expandedRows.includes(index)) {
      setExpandedRows(expandedRows.filter((i) => i !== index));
    } else {
      setExpandedRows([...expandedRows, index]);
    }
  };

  const fmeaData = FMEA_DATA[selectedComponent] || { rpn: 0, failures: [] };

  const getRPNColor = (rpn) => {
    if (rpn > 250) return "text-red-600 bg-red-50";
    if (rpn > 150) return "text-amber-600 bg-amber-50";
    return "text-emerald-600 bg-emerald-50";
  };

  const getRPNBorderColor = (rpn) => {
    if (rpn > 250) return "border-red-200";
    if (rpn > 150) return "border-amber-200";
    return "border-emerald-200";
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-5 h-5 text-orange-500" />
        <h3 className="text-lg font-semibold text-slate-800">
          FMEA Analysis (Failure Mode and Effects Analysis)
        </h3>
      </div>

      {/* Component Selector */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Select Component:
        </label>
        <select
          value={selectedComponent}
          onChange={(e) => setSelectedComponent(e.target.value)}
          className="w-full md:w-64 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {safeComponents.map((comp) => (
            <option key={comp} value={comp}>
              {comp}
            </option>
          ))}
        </select>
      </div>

      {/* RPN Score Badge */}
      <div
        className={`inline-block px-4 py-2 rounded-lg border mb-4 ${getRPNColor(
          fmeaData.rpn
        )} ${getRPNBorderColor(fmeaData.rpn)}`}
      >
        <span className="font-semibold">Overall RPN Score: {fmeaData.rpn}</span>
        <span className="text-xs ml-2">
          {fmeaData.rpn > 250
            ? "(High Risk)"
            : fmeaData.rpn > 150
            ? "(Medium Risk)"
            : "(Low Risk)"}
        </span>
      </div>

      {/* FMEA Table */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-slate-100">
              <th className="border border-slate-300 px-4 py-2 text-left text-sm font-semibold text-slate-700">
                Failure Mode
              </th>
              <th className="border border-slate-300 px-4 py-2 text-left text-sm font-semibold text-slate-700">
                Root Cause
              </th>
              <th className="border border-slate-300 px-4 py-2 text-left text-sm font-semibold text-slate-700">
                Effect
              </th>
              <th className="border border-slate-300 px-4 py-2 text-center text-sm font-semibold text-slate-700">
                S
              </th>
              <th className="border border-slate-300 px-4 py-2 text-center text-sm font-semibold text-slate-700">
                O
              </th>
              <th className="border border-slate-300 px-4 py-2 text-center text-sm font-semibold text-slate-700">
                D
              </th>
              <th className="border border-slate-300 px-4 py-2 text-center text-sm font-semibold text-slate-700">
                RPN
              </th>
              <th className="border border-slate-300 px-4 py-2 text-center text-sm font-semibold text-slate-700">
                Action
              </th>
            </tr>
          </thead>
          <tbody>
            {fmeaData.failures.map((failure, index) => {
              const rpn =
                failure.severity * failure.occurrence * failure.detection;
              const isExpanded = expandedRows.includes(index);

              return (
                <React.Fragment key={index}>
                  <tr className="hover:bg-slate-50 transition-colors">
                    <td className="border border-slate-300 px-4 py-2 text-sm text-slate-800">
                      {failure.mode}
                    </td>
                    <td className="border border-slate-300 px-4 py-2 text-sm text-slate-800">
                      {failure.cause}
                    </td>
                    <td className="border border-slate-300 px-4 py-2 text-sm text-slate-800">
                      {failure.effect}
                    </td>
                    <td className="border border-slate-300 px-4 py-2 text-center text-sm font-semibold text-slate-700">
                      {failure.severity}
                    </td>
                    <td className="border border-slate-300 px-4 py-2 text-center text-sm font-semibold text-slate-700">
                      {failure.occurrence}
                    </td>
                    <td className="border border-slate-300 px-4 py-2 text-center text-sm font-semibold text-slate-700">
                      {failure.detection}
                    </td>
                    <td
                      className={`border border-slate-300 px-4 py-2 text-center text-sm font-bold ${
                        rpn > 250
                          ? "text-red-600"
                          : rpn > 150
                          ? "text-amber-600"
                          : "text-emerald-600"
                      }`}
                    >
                      {rpn}
                    </td>
                    <td className="border border-slate-300 px-4 py-2 text-center">
                      <button
                        onClick={() => toggleRow(index)}
                        className="text-blue-600 hover:text-blue-700 transition-colors"
                      >
                        {isExpanded ? (
                          <ChevronUp className="w-5 h-5" />
                        ) : (
                          <ChevronDown className="w-5 h-5" />
                        )}
                      </button>
                    </td>
                  </tr>
                  {isExpanded && (
                    <tr>
                      <td
                        colSpan="8"
                        className="border border-slate-300 bg-blue-50 px-4 py-3"
                      >
                        <div className="text-sm">
                          <p className="font-semibold text-slate-800 mb-2">
                            Recommended Actions:
                          </p>
                          <ul className="list-disc list-inside space-y-1 text-slate-700">
                            {rpn > 250 && (
                              <>
                                <li>
                                  Immediate preventive maintenance required
                                </li>
                                <li>
                                  Implement monitoring system for early
                                  detection
                                </li>
                                <li>
                                  Schedule component replacement or repair
                                </li>
                              </>
                            )}
                            {rpn <= 250 && rpn > 150 && (
                              <>
                                <li>Schedule regular maintenance checks</li>
                                <li>Monitor performance trends closely</li>
                                <li>Prepare spare parts inventory</li>
                              </>
                            )}
                            {rpn <= 150 && (
                              <>
                                <li>Continue routine maintenance schedule</li>
                                <li>Monitor as part of regular inspection</li>
                              </>
                            )}
                          </ul>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="mt-4 text-xs text-slate-600 space-y-1">
        <p>
          <strong>S (Severity):</strong> How severe is the effect on the
          customer (1-10)
        </p>
        <p>
          <strong>O (Occurrence):</strong> How frequently does the failure occur
          (1-10)
        </p>
        <p>
          <strong>D (Detection):</strong> How difficult is it to detect the
          failure (1-10)
        </p>
        <p>
          <strong>RPN (Risk Priority Number):</strong> S × O × D (Higher = More
          critical)
        </p>
      </div>
    </div>
  );
};

export default FMEATable;
