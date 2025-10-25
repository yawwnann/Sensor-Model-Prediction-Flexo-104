/**
 * AuthPage Component
 *
 * Halaman authentication yang menggabungkan login dan register
 */

import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import Login from "../components/Login";
import Register from "../components/Register";
import { Settings } from "lucide-react";

const AuthPage = () => {
  const [currentMode, setCurrentMode] = useState("login");
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSwitchMode = () => {
    setCurrentMode(currentMode === "login" ? "register" : "login");
  };

  const handleRegisterSuccess = () => {
    // After successful registration, switch to login
    setCurrentMode("login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="bg-slate-800 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <Settings className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">FlexoTwin</h1>
          <p className="text-slate-600">
            Digital Twin System for Flexo Machine Monitoring
          </p>
        </div>

        {/* Auth Component */}
        {currentMode === "login" ? (
          <Login onSwitchToRegister={handleSwitchMode} />
        ) : (
          <Register
            onSuccess={handleRegisterSuccess}
            onSwitchToLogin={handleSwitchMode}
          />
        )}

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-xs text-slate-500">
            © 2024 FlexoTwin. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
