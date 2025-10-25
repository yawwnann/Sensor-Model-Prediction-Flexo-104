/**
 * AuthModal Component
 *
 * Modal yang menggabungkan Login dan Register dalam satu interface
 */

import { useState } from "react";
import { X } from "lucide-react";
import Login from "./Login";
import Register from "./Register";

const AuthModal = ({
  isOpen,
  onClose,
  onAuthSuccess,
  initialMode = "login",
}) => {
  const [currentMode, setCurrentMode] = useState(initialMode);

  if (!isOpen) return null;

  const handleAuthSuccess = (user) => {
    if (onAuthSuccess) {
      onAuthSuccess(user);
    }
    onClose();
  };

  const handleSwitchMode = () => {
    setCurrentMode(currentMode === "login" ? "register" : "login");
  };

  const handleRegisterSuccess = () => {
    // After successful registration, switch to login
    setCurrentMode("login");
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal Container */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative max-w-md w-full">
          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute -top-3 -right-3 z-10 bg-white rounded-full p-2 shadow-lg hover:bg-slate-50 transition-colors"
          >
            <X className="w-5 h-5 text-slate-600" />
          </button>

          {/* Auth Component */}
          {currentMode === "login" ? (
            <Login
              onSuccess={handleAuthSuccess}
              onSwitchToRegister={handleSwitchMode}
            />
          ) : (
            <Register
              onSuccess={handleRegisterSuccess}
              onSwitchToLogin={handleSwitchMode}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
