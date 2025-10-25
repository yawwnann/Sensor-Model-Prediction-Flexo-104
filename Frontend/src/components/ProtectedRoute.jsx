/**
 * ProtectedRoute Component
 *
 * Wrapper component untuk melindungi rute yang memerlukan authentication
 */

import { useAuth } from "../contexts/AuthContext";
import { Navigate, useLocation } from "react-router-dom";
import { Loader } from "lucide-react";

const ProtectedRoute = ({
  children,
  requireRole = null,
  fallbackPath = "/auth",
}) => {
  const { user, isLoading, isAuthenticated } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <Loader className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-slate-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Redirect to auth if not authenticated
  if (!isAuthenticated) {
    return <Navigate to={fallbackPath} state={{ from: location }} replace />;
  }

  // Check role requirements if specified
  if (requireRole && user?.role !== requireRole) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-8 text-center max-w-md w-full mx-4">
          <div className="bg-red-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.1c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">
            Access Denied
          </h2>
          <p className="text-slate-600 mb-4">
            You don't have permission to access this page.
          </p>
          <p className="text-sm text-slate-500">
            Required role: <span className="font-semibold">{requireRole}</span>
            <br />
            Your role:{" "}
            <span className="font-semibold">{user?.role || "Unknown"}</span>
          </p>
        </div>
      </div>
    );
  }

  // User is authenticated and has required role (if any)
  return children;
};

export default ProtectedRoute;
