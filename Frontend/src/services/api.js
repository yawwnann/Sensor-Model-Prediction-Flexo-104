import axios from "axios";

const BASE_URL = "http://localhost:5000/api";

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10 seconds
});

// Add request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error("[API Error]", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Fetch health data for a specific component
 * @param {string} componentName - Name of the component (e.g., "Pre-Feeder")
 * @returns {Promise<Object>} Component health data
 */
export const fetchComponentHealth = async (componentName) => {
  try {
    const response = await apiClient.get(`/health/${componentName}`);
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    return {
      success: false,
      error:
        error.response?.data?.error ||
        error.message ||
        "Failed to fetch component health",
    };
  }
};

/**
 * Run maintenance prediction
 * @param {Object} payload - Prediction input data
 * @param {number} payload.total_produksi - Total production count
 * @param {number} payload.produk_cacat - Defect count
 * @returns {Promise<Object>} Prediction result
 */
export const runMaintenancePrediction = async (payload) => {
  try {
    const response = await apiClient.post("/predict/maintenance", payload);
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    return {
      success: false,
      error:
        error.response?.data?.error ||
        error.message ||
        "Failed to run prediction",
    };
  }
};

/**
 * Fetch health data for all components in parallel
 * @param {string[]} components - Array of component names
 * @returns {Promise<Object>} Object with component names as keys
 */
export const fetchAllComponentsHealth = async (components) => {
  try {
    const promises = components.map((component) =>
      fetchComponentHealth(component)
    );

    const results = await Promise.allSettled(promises);

    const healthData = {};
    components.forEach((component, index) => {
      const result = results[index];
      if (result.status === "fulfilled" && result.value.success) {
        healthData[component] = result.value.data;
      } else {
        healthData[component] = {
          error: result.reason?.message || "Failed to fetch data",
        };
      }
    });

    return healthData;
  } catch (error) {
    console.error("Error fetching all components:", error);
    throw error;
  }
};

export default apiClient;
