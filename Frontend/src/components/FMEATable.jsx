import React, { useState } from "react";
import { AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";

// FMEA Static Data
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
  const [selectedComponent, setSelectedComponent] = useState(
    components[0] || "Pre-Feeder"
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
    if (rpn > 150) return "text-yellow-600 bg-yellow-50";
    return "text-green-600 bg-green-50";
  };

  const getRPNBorderColor = (rpn) => {
    if (rpn > 250) return "border-red-300";
    if (rpn > 150) return "border-yellow-300";
    return "border-green-300";
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border-2 border-gray-200">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-5 h-5 text-orange-600" />
        <h3 className="text-lg font-semibold text-gray-800">
          FMEA Analysis (Failure Mode and Effects Analysis)
        </h3>
      </div>

      {/* Component Selector */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Component:
        </label>
        <select
          value={selectedComponent}
          onChange={(e) => setSelectedComponent(e.target.value)}
          className="w-full md:w-64 px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        >
          {components.map((comp) => (
            <option key={comp} value={comp}>
              {comp}
            </option>
          ))}
        </select>
      </div>

      {/* RPN Score Badge */}
      <div
        className={`inline-block px-4 py-2 rounded-lg border-2 mb-4 ${getRPNColor(
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
            <tr className="bg-gray-100">
              <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold text-gray-700">
                Failure Mode
              </th>
              <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold text-gray-700">
                Root Cause
              </th>
              <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold text-gray-700">
                Effect
              </th>
              <th className="border border-gray-300 px-4 py-2 text-center text-sm font-semibold text-gray-700">
                S
              </th>
              <th className="border border-gray-300 px-4 py-2 text-center text-sm font-semibold text-gray-700">
                O
              </th>
              <th className="border border-gray-300 px-4 py-2 text-center text-sm font-semibold text-gray-700">
                D
              </th>
              <th className="border border-gray-300 px-4 py-2 text-center text-sm font-semibold text-gray-700">
                RPN
              </th>
              <th className="border border-gray-300 px-4 py-2 text-center text-sm font-semibold text-gray-700">
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
                  <tr className="hover:bg-gray-50 transition-colors">
                    <td className="border border-gray-300 px-4 py-2 text-sm">
                      {failure.mode}
                    </td>
                    <td className="border border-gray-300 px-4 py-2 text-sm">
                      {failure.cause}
                    </td>
                    <td className="border border-gray-300 px-4 py-2 text-sm">
                      {failure.effect}
                    </td>
                    <td className="border border-gray-300 px-4 py-2 text-center text-sm font-semibold">
                      {failure.severity}
                    </td>
                    <td className="border border-gray-300 px-4 py-2 text-center text-sm font-semibold">
                      {failure.occurrence}
                    </td>
                    <td className="border border-gray-300 px-4 py-2 text-center text-sm font-semibold">
                      {failure.detection}
                    </td>
                    <td
                      className={`border border-gray-300 px-4 py-2 text-center text-sm font-bold ${
                        rpn > 250
                          ? "text-red-600"
                          : rpn > 150
                          ? "text-yellow-600"
                          : "text-green-600"
                      }`}
                    >
                      {rpn}
                    </td>
                    <td className="border border-gray-300 px-4 py-2 text-center">
                      <button
                        onClick={() => toggleRow(index)}
                        className="text-indigo-600 hover:text-indigo-800 transition-colors"
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
                        className="border border-gray-300 bg-blue-50 px-4 py-3"
                      >
                        <div className="text-sm">
                          <p className="font-semibold text-gray-800 mb-2">
                            📋 Recommended Actions:
                          </p>
                          <ul className="list-disc list-inside space-y-1 text-gray-700">
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
      <div className="mt-4 text-xs text-gray-600 space-y-1">
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
