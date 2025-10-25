import React, { useState, useRef, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  Bell,
  BellOff,
  UserCircle,
  Menu,
  X,
  BarChart3,
  Target,
  Wifi,
  WifiOff,
  Loader2,
  User,
  LogOut,
  Activity,
  Settings,
  RefreshCw,
} from "lucide-react";
import axios from "axios";
import { useNotification } from "../contexts/NotificationContext";
import { useAuth } from "../contexts/AuthContext";
import UserMenu from "./UserMenu";

/**
 * Navbar Component
 *
 * Navigation bar dengan features:
 * - Machine ID display (C_FL104)
 * - Overall health indicator
 * - Connection status to backend
 * - Manual refresh button
 * - Last update timestamp
 * - Toggle notification on/off
 *
 * Overall health menunjukkan kondisi keseluruhan mesin C_FL104
 */

const API_BASE_URL = "http://localhost:5000/api";

export default function Navbar({
  lastUpdate,
  overallHealth,
  isRefreshing,
  onRefresh,
}) {
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);

  // Get auth context
  const { user } = useAuth();

  // Get notification context
  const { notificationsEnabled, toggleNotifications } = useNotification();

  // Connection status state
  const [connectionStatus, setConnectionStatus] = useState("checking"); // 'checking', 'connected', 'disconnected'
  const [lastChecked, setLastChecked] = useState(null);

  const notifMenuRef = useRef(null);

  // Check backend connection
  const checkConnection = async () => {
    try {
      setConnectionStatus("checking");
      const response = await axios.get(`${API_BASE_URL}/health`, {
        timeout: 5000,
      });
      if (response.status === 200) {
        setConnectionStatus("connected");
        setLastChecked(new Date());
      } else {
        setConnectionStatus("disconnected");
      }
    } catch (error) {
      console.error("Connection check failed:", error);
      setConnectionStatus("disconnected");
      setLastChecked(new Date());
    }
  };

  // Initial connection check and periodic refresh
  useEffect(() => {
    checkConnection();

    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    function onDocClick(e) {
      if (notifMenuRef.current && !notifMenuRef.current.contains(e.target)) {
        setNotifOpen(false);
      }
    }
    document.addEventListener("click", onDocClick);
    return () => document.removeEventListener("click", onDocClick);
  }, []);

  const handleNavClick = (path) => {
    navigate(path);
    setMobileOpen(false);
  };

  return (
    <header className="bg-white shadow-sm border-b border-slate-200 sticky top-0 z-40">
      {/* Top Navigation Bar */}
      <div className="border-b border-slate-100">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            {/* Left: Logo & Brand */}
            <div className="flex items-center gap-4">
              <img
                src="/dtfm2.png"
                alt="FlexoTwin Logo"
                className="w-10 h-10"
              />
              <div>
                <h1 className="text-lg font-bold text-slate-900">FlexoTwin</h1>
                <p className="text-xs text-slate-500">Digital Twin System</p>
              </div>
            </div>

            {/* Center: Navigation */}
            <nav className="hidden md:flex items-center gap-2">
              <button
                onClick={() => handleNavClick("/dashboard")}
                className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors ${
                  location.pathname === "/dashboard"
                    ? "bg-blue-50 text-blue-600"
                    : "text-slate-600 hover:bg-slate-50"
                }`}
              >
                <BarChart3 className="w-4 h-4" />
                Dashboard
              </button>
            </nav>

            {/* Right: User Menu & Actions */}
            <div className="flex items-center gap-3">
              {/* Connection Status */}
              <div className="hidden sm:flex items-center">
                {connectionStatus === "checking" && (
                  <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200">
                    <Loader2 className="w-4 h-4 text-slate-600 animate-spin" />
                    <span className="text-xs font-medium text-slate-600">
                      Checking...
                    </span>
                  </div>
                )}

                {connectionStatus === "connected" && (
                  <div
                    className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-50 border border-green-200 cursor-pointer hover:bg-green-100 transition-colors"
                    title={`Connected to backend\nLast checked: ${lastChecked?.toLocaleTimeString()}`}
                    onClick={checkConnection}
                  >
                    <div className="relative">
                      <Wifi className="w-4 h-4 text-green-600" />
                      <div className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    </div>
                    <span className="text-xs font-semibold text-green-700">
                      Connected
                    </span>
                  </div>
                )}

                {connectionStatus === "disconnected" && (
                  <div
                    className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-50 border border-red-200 cursor-pointer hover:bg-red-100 transition-colors"
                    title="Backend disconnected. Click to retry"
                    onClick={checkConnection}
                  >
                    <WifiOff className="w-4 h-4 text-red-600" />
                    <span className="text-xs font-semibold text-red-700">
                      Disconnected
                    </span>
                  </div>
                )}
              </div>

              {/* Notifications */}
              <div className="relative" ref={notifMenuRef}>
                <button
                  onClick={() => {
                    setNotifOpen((s) => !s);
                  }}
                  className={`relative p-2 rounded-lg transition-colors ${
                    notificationsEnabled
                      ? "hover:bg-slate-100 text-slate-600"
                      : "hover:bg-red-50 text-red-600"
                  }`}
                  aria-label="Notifications"
                  title={
                    notificationsEnabled
                      ? "Notifications enabled"
                      : "Notifications disabled"
                  }
                >
                  {notificationsEnabled ? (
                    <Bell className="w-5 h-5" />
                  ) : (
                    <BellOff className="w-5 h-5" />
                  )}
                  {notificationsEnabled && (
                    <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                  )}
                </button>
                {notifOpen && (
                  <div className="absolute right-0 mt-2 w-72 bg-white border border-slate-200 rounded-lg shadow-lg z-50">
                    <div className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-sm font-semibold text-slate-700">
                          Notification Settings
                        </h3>
                        <button
                          onClick={() => setNotifOpen(false)}
                          className="text-slate-400 hover:text-slate-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>

                      {/* Toggle Switch */}
                      <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg mb-3">
                        <div className="flex items-center gap-2">
                          {notificationsEnabled ? (
                            <Bell className="w-4 h-4 text-blue-600" />
                          ) : (
                            <BellOff className="w-4 h-4 text-slate-400" />
                          )}
                          <div>
                            <p className="text-sm font-medium text-slate-700">
                              Alert Popups
                            </p>
                            <p className="text-xs text-slate-500">
                              Auto-prediction alerts
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={toggleNotifications}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            notificationsEnabled
                              ? "bg-blue-600"
                              : "bg-slate-300"
                          }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              notificationsEnabled
                                ? "translate-x-6"
                                : "translate-x-1"
                            }`}
                          />
                        </button>
                      </div>

                      {/* Status Message */}
                      <div
                        className={`p-3 rounded-lg text-xs ${
                          notificationsEnabled
                            ? "bg-green-50 text-green-700 border border-green-200"
                            : "bg-red-50 text-red-700 border border-red-200"
                        }`}
                      >
                        {notificationsEnabled ? (
                          <div className="flex items-start gap-2">
                            <Bell className="w-4 h-4 mt-0.5 flex-shrink-0" />
                            <div>
                              <p className="font-medium">
                                Notifications Active
                              </p>
                              <p className="mt-1 text-green-600">
                                You'll receive alerts when machine health is
                                critical
                              </p>
                            </div>
                          </div>
                        ) : (
                          <div className="flex items-start gap-2">
                            <BellOff className="w-4 h-4 mt-0.5 flex-shrink-0" />
                            <div>
                              <p className="font-medium">
                                Notifications Disabled
                              </p>
                              <p className="mt-1 text-red-600">
                                Auto-prediction alert popups are hidden
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* User Menu */}
              <UserMenu />
            </div>
          </div>
        </div>
      </div>

      {/* Dashboard Info Bar - Only show on dashboard page */}
      {location.pathname === "/dashboard" && (
        <div className="bg-gradient-to-r from-slate-50 to-slate-100">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between flex-wrap gap-4">
              {/* Left: Page Title & Description */}
              <div className="flex items-center gap-3">
                <div className="bg-slate-800 p-2 rounded-lg">
                  <Settings className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-slate-900">
                    Smart Maintenance Dashboard
                  </h2>
                  <p className="text-sm text-slate-600 flex items-center gap-2 mt-0.5">
                    <Activity className="w-3.5 h-3.5" />
                    <span>
                      Last updated:{" "}
                      {lastUpdate
                        ? lastUpdate.toLocaleTimeString()
                        : "Loading..."}
                    </span>
                    <span className="text-slate-400">|</span>
                    <span>Auto-refresh every 5s</span>
                  </p>
                </div>
              </div>

              {/* Right: Overall Health & Refresh */}
              <div className="flex items-center gap-3">
                <div className="bg-white rounded-lg px-5 py-3 border border-slate-200 shadow-sm">
                  <p className="text-xs text-slate-600 font-medium mb-1">
                    Overall Health
                  </p>
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        overallHealth >= 80
                          ? "bg-green-500"
                          : overallHealth >= 60
                          ? "bg-yellow-500"
                          : "bg-red-500"
                      }`}
                    ></div>
                    <p className="text-2xl font-bold text-slate-900">
                      {overallHealth ? overallHealth.toFixed(1) : "0.0"}%
                    </p>
                  </div>
                </div>

                <button
                  onClick={onRefresh}
                  disabled={isRefreshing}
                  className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-3 rounded-lg flex items-center gap-2 transition-all disabled:opacity-50 shadow-sm"
                >
                  <RefreshCw
                    className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`}
                  />
                  <span className="font-medium">Refresh</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-slate-100 bg-white">
          <div className="px-2 pt-2 pb-3 space-y-1">
            <button
              onClick={() => handleNavClick("/dashboard")}
              className={`w-full text-left px-3 py-2 rounded-md text-base font-medium flex items-center space-x-2 ${
                location.pathname === "/dashboard"
                  ? "bg-blue-100 text-blue-700"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Dashboard</span>
            </button>
            <button
              onClick={() => {
                setMobileOpen(false);
              }}
              className="w-full text-left px-3 py-2 rounded-md text-base font-medium text-red-600 hover:bg-red-50 flex items-center gap-2"
            >
              <LogOut className="w-4 h-4" />
              Access UserMenu for logout
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
