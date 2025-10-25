import { useState, useEffect } from "react";
import ComponentCard from "../components/ComponentCard";
import OEEChart from "../components/OEEChart";
import TrendChart from "../components/TrendChart";
import FMEATable from "../components/FMEATable";
import AutoPredictionAlert from "../components/AutoPredictionAlert";
import DowntimeHistory from "../components/DowntimeHistory";
import Hotspot from "../components/Hotspot";
import HotspotPopover from "../components/HotspotPopover";
import Navbar from "../components/Navbar";
import { fetchAllComponentsHealth } from "../services/api";
import {
  AlertTriangle,
  Activity,
  BarChart3,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

/**
 * DashboardPage - Main Monitoring Dashboard for Flexo Machine C_FL104
 * 
 * Features:
 * - Real-time health monitoring untuk semua komponen
 * - Auto-prediction alert ketika overall machine health < 40%
 * - Interactive machine diagram dengan hotspots
 * - Health trends & OEE charts
 * - FMEA analysis table
 * 
 * Note: Auto-prediction memprediksi maintenance duration untuk
 * KESELURUHAN MESIN C_FL104, bukan per komponen individual.
 * 
 * Sesuai dengan DOKUMENTASI.md - Model ML memprediksi total
 * maintenance time untuk seluruh mesin.
 */

// Machine Components untuk Flexo C_FL104
const COMPONENTS = ["Pre-Feeder", "Feeder", "Printing", "Slotter", "Stacker"];

// Refresh interval untuk real-time monitoring (5 detik)
const REFRESH_INTERVAL = 5000;

// Hotspot positions for main machine diagram (Slide 1)
const hotspotConfig = [
  {
    id: 1,
    x: 15,
    y: 55,
    label: "Pre-Feeder",
    componentName: "Pre-Feeder",
  },
  {
    id: 2,
    x: 25,
    y: 55,
    label: "Feeder",
    componentName: "Feeder",
  },
  {
    id: 3,
    x: 50,
    y: 55,
    label: "Printing",
    componentName: "Printing",
  },
  {
    id: 4,
    x: 70,
    y: 55,
    label: "Slotter",
    componentName: "Slotter",
  },
  {
    id: 5,
    x: 85,
    y: 55,
    label: "Stacker",
    componentName: "Stacker",
  },
];

// Hotspot positions for Slide 2 - Pre-Feeder & Feeder
const slide2Hotspots = [
  {
    id: 1,
    x: 50,
    y: 50,
    label: "Pre-Feeder",
    componentName: "Pre-Feeder",
  },
  {
    id: 2,
    x: 65,
    y: 50,
    label: "Feeder",
    componentName: "Feeder",
  },
];

// Hotspot positions for Slide 3 - Printing Unit
const slide3Hotspots = [
  {
    id: 1,
    x: 50,
    y: 50,
    label: "Printing Unit",
    componentName: "Printing",
  },
];

// Hotspot positions for Slide 4 - Slotter
const slide4Hotspots = [
  {
    id: 1,
    x: 50,
    y: 50,
    label: "Slotter",
    componentName: "Slotter",
  },
];

// Hotspot positions for Slide 5 - Stacker
const slide5Hotspots = [
  {
    id: 1,
    x: 50,
    y: 50,
    label: "Stacker",
    componentName: "Stacker",
  },
];

function DashboardPage() {
  const [healthData, setHealthData] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [hoveredHotspot, setHoveredHotspot] = useState(null);
  const [currentSlide, setCurrentSlide] = useState(0);
  const totalSlides = 5;

  // Historical data for trends
  const [healthHistory, setHealthHistory] = useState({
    "Pre-Feeder": [],
    Feeder: [],
    Printing: [],
    Slotter: [],
    Stacker: [],
  });
  const [oeeHistory, setOeeHistory] = useState([]);
  const [timestamps, setTimestamps] = useState([]);

  // Fetch health data for all components
  const fetchData = async () => {
    try {
      setIsRefreshing(true);
      setError(null);

      const data = await fetchAllComponentsHealth(COMPONENTS);
      setHealthData(data);
      setLastUpdate(new Date());

      // Collect OEE data first
      const newOeeData = [];
      COMPONENTS.forEach((component) => {
        if (data[component] && !data[component].error) {
          const metrics = data[component].metrics || {};
          newOeeData.push({
            oee: metrics.oee_score || 0,
            availability: metrics.availability_rate || 0,
            performance: metrics.performance_rate || 0,
            quality: metrics.quality_rate || 0,
          });
        }
      });

      // Update health history for each component using functional update
      setHealthHistory((prevHistory) => {
        const updatedHistory = { ...prevHistory };
        
        COMPONENTS.forEach((component) => {
          if (data[component] && !data[component].error) {
            const health = data[component].health_index || 0;
            updatedHistory[component] = [
              ...(prevHistory[component] || []),
              health,
            ].slice(-50); // Keep last 50 points
          }
        });
        
        return updatedHistory;
      });

      // Calculate average OEE and add to history
      if (newOeeData.length > 0) {
        const avgOEE = {
          oee:
            newOeeData.reduce((sum, d) => sum + d.oee, 0) / newOeeData.length,
          availability:
            newOeeData.reduce((sum, d) => sum + d.availability, 0) /
            newOeeData.length,
          performance:
            newOeeData.reduce((sum, d) => sum + d.performance, 0) /
            newOeeData.length,
          quality:
            newOeeData.reduce((sum, d) => sum + d.quality, 0) /
            newOeeData.length,
        };
        setOeeHistory((prev) => [...prev, avgOEE].slice(-50)); // Keep last 50 points
      }

      // Add timestamp
      setTimestamps((prev) =>
        [...prev, new Date().toLocaleTimeString()].slice(-50)
      );

      setIsLoading(false);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError(
        "Failed to connect to backend. Please ensure the Flask server is running on http://localhost:5000"
      );
      setIsLoading(false);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Initial fetch and setup interval
  useEffect(() => {
    fetchData();

    const interval = setInterval(() => {
      fetchData();
    }, REFRESH_INTERVAL);

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Manual refresh handler
  const handleManualRefresh = () => {
    fetchData();
  };

  // Carousel handlers
  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % totalSlides);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + totalSlides) % totalSlides);
  };

  const goToSlide = (index) => {
    setCurrentSlide(index);
  };

  // Calculate overall health
  const calculateOverallHealth = () => {
    const healthValues = Object.values(healthData)
      .filter((data) => !data.error && data.health_index)
      .map((data) => data.health_index);

    if (healthValues.length === 0) return 0;

    return (
      healthValues.reduce((sum, val) => sum + val, 0) / healthValues.length
    );
  };

  const overallHealth = calculateOverallHealth();

  // Get health data for hovered hotspot
  const hoveredHealthData = hoveredHotspot
    ? healthData[hoveredHotspot.componentName]
    : null;

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navbar */}
      <Navbar 
        lastUpdate={lastUpdate}
        overallHealth={overallHealth}
        isRefreshing={isRefreshing}
        onRefresh={handleManualRefresh}
      />

      {/* Auto-Prediction Alert */}
      <AutoPredictionAlert healthData={healthData} />

      <main className="container mx-auto px-6 py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900 mb-1">
                Connection Error
              </h3>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Machine Diagram Section */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Activity className="w-6 h-6" />
            Machine Overview
          </h2>
          <div className="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
            {/* Carousel Header */}
            <div className="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="bg-white/10 p-2 rounded-lg backdrop-blur-sm">
                  <Activity className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-white font-semibold text-lg">Flexo Machine</h3>
                  <p className="text-slate-300 text-sm">
                    View {currentSlide + 1}/{totalSlides}
                  </p>
                </div>
              </div>
              
              {/* Navigation Arrows */}
              <div className="flex items-center gap-2">
                <button
                  onClick={prevSlide}
                  className="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-all"
                  aria-label="Previous view"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={nextSlide}
                  className="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-all"
                  aria-label="Next view"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Carousel Content */}
            <div className="relative">
              {/* Slides Container */}
              <div className="relative w-full h-[500px] bg-slate-100 overflow-hidden">
                {/* Slide 1 - Main Machine View */}
                <div
                  className={`absolute inset-0 transition-transform duration-500 ease-in-out ${
                    currentSlide === 0 ? 'translate-x-0' : '-translate-x-full'
                  }`}
                >
                  <div className="relative w-full h-full">
                    {/* Machine Diagram Image */}
                    <img
                      src="/FullFlexo.png"
                      alt="Flexo Machine Diagram"
                      className="absolute inset-0 w-full h-full object-contain p-4"
                      onError={(e) => {
                        e.target.style.display = 'none';
                      }}
                    />
                    
                    {/* Fallback line if image not available */}
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                      <div className="w-full h-2 mx-8 opacity-20"></div>
                    </div>

                    {/* Hotspots */}
                    {hotspotConfig.map((hotspot) => {
                      const componentHealth = healthData[hotspot.componentName];
                      return (
                        <Hotspot
                          key={hotspot.id}
                          x={hotspot.x}
                          y={hotspot.y}
                          label={hotspot.label}
                          status={
                            componentHealth?.error
                              ? "error"
                              : componentHealth?.health_index >= 80
                              ? "good"
                              : componentHealth?.health_index >= 60
                              ? "warning"
                              : "critical"
                          }
                          isActive={hoveredHotspot?.id === hotspot.id}
                          onMouseEnter={() => setHoveredHotspot(hotspot)}
                          onMouseLeave={() => setHoveredHotspot(null)}
                        />
                      );
                    })}

                    {/* Hotspot Popover */}
                    {hoveredHotspot && hoveredHealthData && (
                      <HotspotPopover
                        x={hoveredHotspot.x}
                        y={hoveredHotspot.y}
                        data={{
                          name: hoveredHotspot.label,
                          health: hoveredHealthData.health_index || 0,
                          status: hoveredHealthData.status || "Unknown",
                          oee: hoveredHealthData.metrics?.oee_score || 0,
                        }}
                      />
                    )}
                  </div>
                </div>

                {/* Slide 2 - Pre-Feeder & Feeder View */}
                <div
                  className={`absolute inset-0 transition-transform duration-500 ease-in-out ${
                    currentSlide === 1
                      ? 'translate-x-0'
                      : currentSlide < 1
                      ? 'translate-x-full'
                      : '-translate-x-full'
                  }`}
                >
                  <div className="relative w-full h-full bg-slate-50">
                    <img
                      src="/PreFeeder&Feeder.png"
                      alt="Pre-Feeder & Feeder Unit"
                      className="absolute inset-0 w-full h-full object-contain p-4"
                    />

                    {/* Hotspots for Slide 2 */}
                    {slide2Hotspots.map((hotspot) => {
                      const componentHealth = healthData[hotspot.componentName];
                      return (
                        <Hotspot
                          key={hotspot.id}
                          x={hotspot.x}
                          y={hotspot.y}
                          label={hotspot.label}
                          status={
                            componentHealth?.error
                              ? "error"
                              : componentHealth?.health_index >= 80
                              ? "good"
                              : componentHealth?.health_index >= 60
                              ? "warning"
                              : "critical"
                          }
                          isActive={hoveredHotspot?.id === hotspot.id && currentSlide === 1}
                          onMouseEnter={() => setHoveredHotspot(hotspot)}
                          onMouseLeave={() => setHoveredHotspot(null)}
                        />
                      );
                    })}

                    {/* Hotspot Popover */}
                    {hoveredHotspot && currentSlide === 1 && (() => {
                      const componentHealth = healthData[hoveredHotspot.componentName];
                      return componentHealth && (
                        <HotspotPopover
                          x={hoveredHotspot.x}
                          y={hoveredHotspot.y}
                          data={{
                            name: hoveredHotspot.label,
                            health: componentHealth.health_index || 0,
                            status: componentHealth.status || "Unknown",
                            oee: componentHealth.metrics?.oee_score || 0,
                          }}
                        />
                      );
                    })()}

                    <div className="absolute bottom-8 left-1/2 -translate-x-1/2 bg-black/60 backdrop-blur-sm px-6 py-3 rounded-lg">
                      <h4 className="text-white font-semibold text-center">
                        Pre-Feeder & Feeder Unit
                      </h4>
                      <p className="text-slate-300 text-sm text-center mt-1">
                        Material feeding system
                      </p>
                    </div>
                  </div>
                </div>

                {/* Slide 3 - Printing Unit View */}
                <div
                  className={`absolute inset-0 transition-transform duration-500 ease-in-out ${
                    currentSlide === 2
                      ? 'translate-x-0'
                      : currentSlide < 2
                      ? 'translate-x-full'
                      : '-translate-x-full'
                  }`}
                >
                  <div className="relative w-full h-full bg-slate-50">
                    <img
                      src="/PrintingUnit.png"
                      alt="Printing Unit"
                      className="absolute inset-0 w-full h-full object-contain p-4"
                    />

                    {/* Hotspots for Slide 3 */}
                    {slide3Hotspots.map((hotspot) => {
                      const componentHealth = healthData[hotspot.componentName];
                      return (
                        <Hotspot
                          key={hotspot.id}
                          x={hotspot.x}
                          y={hotspot.y}
                          label={hotspot.label}
                          status={
                            componentHealth?.error
                              ? "error"
                              : componentHealth?.health_index >= 80
                              ? "good"
                              : componentHealth?.health_index >= 60
                              ? "warning"
                              : "critical"
                          }
                          isActive={hoveredHotspot?.id === hotspot.id && currentSlide === 2}
                          onMouseEnter={() => setHoveredHotspot(hotspot)}
                          onMouseLeave={() => setHoveredHotspot(null)}
                        />
                      );
                    })}

                    {/* Hotspot Popover */}
                    {hoveredHotspot && currentSlide === 2 && (() => {
                      const componentHealth = healthData[hoveredHotspot.componentName];
                      return componentHealth && (
                        <HotspotPopover
                          x={hoveredHotspot.x}
                          y={hoveredHotspot.y}
                          data={{
                            name: hoveredHotspot.label,
                            health: componentHealth.health_index || 0,
                            status: componentHealth.status || "Unknown",
                            oee: componentHealth.metrics?.oee_score || 0,
                          }}
                        />
                      );
                    })()}

                    <div className="absolute bottom-8 left-1/2 -translate-x-1/2 bg-black/60 backdrop-blur-sm px-6 py-3 rounded-lg">
                      <h4 className="text-white font-semibold text-center">
                        Printing Unit
                      </h4>
                      <p className="text-slate-300 text-sm text-center mt-1">
                        Multi-color flexographic printing
                      </p>
                    </div>
                  </div>
                </div>

                {/* Slide 4 - Slotter Unit View */}
                <div
                  className={`absolute inset-0 transition-transform duration-500 ease-in-out ${
                    currentSlide === 3
                      ? 'translate-x-0'
                      : currentSlide < 3
                      ? 'translate-x-full'
                      : '-translate-x-full'
                  }`}
                >
                  <div className="relative w-full h-full bg-slate-50">
                    <img
                      src="/Slotter.png"
                      alt="Slotter Unit"
                      className="absolute inset-0 w-full h-full object-contain p-4"
                    />

                    {/* Hotspots for Slide 4 */}
                    {slide4Hotspots.map((hotspot) => {
                      const componentHealth = healthData[hotspot.componentName];
                      return (
                        <Hotspot
                          key={hotspot.id}
                          x={hotspot.x}
                          y={hotspot.y}
                          label={hotspot.label}
                          status={
                            componentHealth?.error
                              ? "error"
                              : componentHealth?.health_index >= 80
                              ? "good"
                              : componentHealth?.health_index >= 60
                              ? "warning"
                              : "critical"
                          }
                          isActive={hoveredHotspot?.id === hotspot.id && currentSlide === 3}
                          onMouseEnter={() => setHoveredHotspot(hotspot)}
                          onMouseLeave={() => setHoveredHotspot(null)}
                        />
                      );
                    })}

                    {/* Hotspot Popover */}
                    {hoveredHotspot && currentSlide === 3 && (() => {
                      const componentHealth = healthData[hoveredHotspot.componentName];
                      return componentHealth && (
                        <HotspotPopover
                          x={hoveredHotspot.x}
                          y={hoveredHotspot.y}
                          data={{
                            name: hoveredHotspot.label,
                            health: componentHealth.health_index || 0,
                            status: componentHealth.status || "Unknown",
                            oee: componentHealth.metrics?.oee_score || 0,
                          }}
                        />
                      );
                    })()}

                    <div className="absolute bottom-8 left-1/2 -translate-x-1/2 bg-black/60 backdrop-blur-sm px-6 py-3 rounded-lg">
                      <h4 className="text-white font-semibold text-center">
                        Slotter Unit
                      </h4>
                      <p className="text-slate-300 text-sm text-center mt-1">
                        Cutting and creasing system
                      </p>
                    </div>
                  </div>
                </div>

                {/* Slide 5 - Stacker Unit View */}
                <div
                  className={`absolute inset-0 transition-transform duration-500 ease-in-out ${
                    currentSlide === 4
                      ? 'translate-x-0'
                      : currentSlide < 4
                      ? 'translate-x-full'
                      : '-translate-x-full'
                  }`}
                >
                  <div className="relative w-full h-full bg-slate-50">
                    <img
                      src="/stacker_2.png"
                      alt="Stacker Unit"
                      className="absolute inset-0 w-full h-full object-contain p-4"
                    />

                    {/* Hotspots for Slide 5 */}
                    {slide5Hotspots.map((hotspot) => {
                      const componentHealth = healthData[hotspot.componentName];
                      return (
                        <Hotspot
                          key={hotspot.id}
                          x={hotspot.x}
                          y={hotspot.y}
                          label={hotspot.label}
                          status={
                            componentHealth?.error
                              ? "error"
                              : componentHealth?.health_index >= 80
                              ? "good"
                              : componentHealth?.health_index >= 60
                              ? "warning"
                              : "critical"
                          }
                          isActive={hoveredHotspot?.id === hotspot.id && currentSlide === 4}
                          onMouseEnter={() => setHoveredHotspot(hotspot)}
                          onMouseLeave={() => setHoveredHotspot(null)}
                        />
                      );
                    })}

                    {/* Hotspot Popover */}
                    {hoveredHotspot && currentSlide === 4 && (() => {
                      const componentHealth = healthData[hoveredHotspot.componentName];
                      return componentHealth && (
                        <HotspotPopover
                          x={hoveredHotspot.x}
                          y={hoveredHotspot.y}
                          data={{
                            name: hoveredHotspot.label,
                            health: componentHealth.health_index || 0,
                            status: componentHealth.status || "Unknown",
                            oee: componentHealth.metrics?.oee_score || 0,
                          }}
                        />
                      );
                    })()}

                    <div className="absolute bottom-8 left-1/2 -translate-x-1/2 bg-black/60 backdrop-blur-sm px-6 py-3 rounded-lg">
                      <h4 className="text-white font-semibold text-center">
                        Stacker Unit
                      </h4>
                      <p className="text-slate-300 text-sm text-center mt-1">
                        Output collection and stacking
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Navigation Dots */}
              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-black/30 backdrop-blur-sm px-4 py-2 rounded-full">
                {Array.from({ length: totalSlides }).map((_, index) => (
                  <button
                    key={index}
                    onClick={() => goToSlide(index)}
                    className={`transition-all rounded-full ${
                      currentSlide === index
                        ? 'bg-white w-8 h-2'
                        : 'bg-white/50 hover:bg-white/75 w-2 h-2'
                    }`}
                    aria-label={`Go to view ${index + 1}`}
                  />
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Component Cards Grid */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <BarChart3 className="w-6 h-6" />
            Component Health Status
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
            {COMPONENTS.map((component) => (
              <ComponentCard
                key={component}
                name={component}
                healthData={healthData[component]}
                isLoading={isLoading}
              />
            ))}
          </div>
        </section>

        {/* Charts Section - Vertical Layout */}
        <div className="space-y-8 mb-8">
          {/* Health Trend Chart */}
          <section>
            <TrendChart
              healthHistory={healthHistory}
              timestamps={timestamps}
            />
          </section>

          {/* OEE Chart */}
          <section>
            <OEEChart 
              componentsData={healthData} 
              oeeHistory={oeeHistory} 
              timestamps={timestamps} 
            />
          </section>
        </div>

        {/* FMEA Table */}
        <section className="mb-8">
          <FMEATable healthData={healthData} />
        </section>

        {/* Downtime History */}
        <section className="mb-8">
          <DowntimeHistory limit={10} />
        </section>
      </main>
    </div>
  );
}

export default DashboardPage;
