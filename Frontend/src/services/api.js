import axios from "axios";

/**
 * API Service for Digital Twin Flexo Machine C_FL104
 * Base URL: http://localhost:5000/api
 * 
 * Dokumentasi Lengkap: DOKUMENTASI.md
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error("[API Request Error]", error);
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    if (error.response) {
      console.error(`[API Error] ${error.response.status}`);
    } else if (error.request) {
      console.error("[API Error] No response received");
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// HEALTH MONITORING APIs
// ============================================================================

export const fetchMachineHealth = async () => {
  try {
    const response = await apiClient.get("/health/machine");
    return response.data;
  } catch (error) {
    console.error("Error fetching machine health:", error);
    throw error;
  }
};

export const fetchComponentsHealth = async () => {
  try {
    const response = await apiClient.get("/health/components");
    return response.data;
  } catch (error) {
    console.error("Error fetching components health:", error);
    throw error;
  }
};

export const fetchComponentHealth = async (componentName) => {
  try {
    const response = await apiClient.get(`/health/${componentName}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching health for ${componentName}:`, error);
    throw error;
  }
};

export const fetchAllComponentsHealth = async (componentNames) => {
  try {
    const promises = componentNames.map((name) => 
      fetchComponentHealth(name).catch(error => ({
        error: `Failed to fetch ${name}: ${error.message}`
      }))
    );
    
    const results = await Promise.all(promises);
    
    const healthData = {};
    componentNames.forEach((name, index) => {
      healthData[name] = results[index];
    });
    
    return healthData;
  } catch (error) {
    console.error("Error fetching all components health:", error);
    throw error;
  }
};

// ============================================================================
// SENSOR DATA APIs
// ============================================================================

export const fetchLatestSensorData = async () => {
  try {
    const response = await apiClient.get("/sensor/latest");
    return response.data;
  } catch (error) {
    console.error("Error fetching latest sensor data:", error);
    throw error;
  }
};

export const fetchSensorHistory = async (limit = 50) => {
  try {
    const response = await apiClient.get("/sensor/history", {
      params: { limit }
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching sensor history:", error);
    throw error;
  }
};

// ============================================================================
// PREDICTION APIs
// ============================================================================

export const predictMaintenance = async (inputData) => {
  try {
    const response = await apiClient.post("/predict/maintenance", {
      machine_id: "C_FL104",
      input_data: inputData
    });
    return response.data;
  } catch (error) {
    console.error("Error predicting maintenance:", error);
    throw error;
  }
};

export const fetchPredictionHistory = async (limit = 20, dateFrom = null) => {
  try {
    const params = { limit };
    if (dateFrom) {
      params.date_from = dateFrom;
    }
    
    const response = await apiClient.get("/predict/history", { params });
    return response.data;
  } catch (error) {
    console.error("Error fetching prediction history:", error);
    throw error;
  }
};

// ============================================================================
// SYSTEM INFO APIs
// ============================================================================

export const fetchSystemInfo = async () => {
  try {
    const response = await apiClient.get("/info");
    return response.data;
  } catch (error) {
    console.error("Error fetching system info:", error);
    throw error;
  }
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

export const checkBackendConnection = async () => {
  try {
    await fetchSystemInfo();
    return true;
  } catch (error) {
    return false;
  }
};

export const formatErrorMessage = (error) => {
  if (error.response) {
    return error.response.data?.message || error.response.data?.error || "Server error occurred";
  } else if (error.request) {
    return "Cannot connect to backend. Please ensure Flask server is running on http://localhost:5000";
  } else {
    return error.message || "An unexpected error occurred";
  }
};

// ============================================================================
// DOWNTIME HISTORY APIs
// ============================================================================

/**
 * GET /api/downtime/history
 * Mendapatkan riwayat downtime mesin dari machine_logs
 * 
 * @param {number} limit - Jumlah record (default: 50)
 * @param {string} component - Filter by component (optional, default: 'all')
 * @param {string} startDate - Start date (format: YYYY-MM-DD)
 * @param {string} endDate - End date (format: YYYY-MM-DD)
 * @returns {Promise<Array>} Array of downtime events
 */
export const fetchDowntimeHistory = async (
  limit = 50,
  component = null,
  startDate = null,
  endDate = null
) => {
  try {
    const queryParams = { limit };
    
    if (component && component !== 'all') {
      queryParams.component = component;
    }
    if (startDate) {
      queryParams.start_date = startDate;
    }
    if (endDate) {
      queryParams.end_date = endDate;
    }
    
    const response = await apiClient.get("/downtime/history", {
      params: queryParams
    });
    
    // Return the data array from response
    return response.data?.data || [];
  } catch (error) {
    console.error("Error fetching downtime history:", error);
    throw error;
  }
};

/**
 * GET /api/downtime/statistics
 * Mendapatkan statistik downtime
 * 
 * @param {string} startDate - Start date (format: YYYY-MM-DD)
 * @param {string} endDate - End date (format: YYYY-MM-DD)
 * @returns {Promise<Object>} Statistics object
 */
export const fetchDowntimeStatistics = async (startDate = null, endDate = null) => {
  try {
    const queryParams = {};
    
    if (startDate) {
      queryParams.start_date = startDate;
    }
    if (endDate) {
      queryParams.end_date = endDate;
    }
    
    const response = await apiClient.get("/downtime/statistics", { 
      params: queryParams 
    });
    
    // Return the data object from response
    return response.data?.data || null;
  } catch (error) {
    console.error("Error fetching downtime statistics:", error);
    throw error;
  }
};

export default apiClient;
