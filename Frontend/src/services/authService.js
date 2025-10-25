/**
 * Authentication Service
 *
 * Service untuk menangani authentication di frontend:
 * - Login/logout
 * - Token management
 * - API calls dengan authentication
 */

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

class AuthService {
  constructor() {
    this.token = localStorage.getItem("auth_token");
    this.user = JSON.parse(localStorage.getItem("auth_user") || "null");
  }

  /**
   * Login user
   */
  async login(username, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        this.token = data.data.token;
        this.user = data.data.user;

        // Save to localStorage
        localStorage.setItem("auth_token", this.token);
        localStorage.setItem("auth_user", JSON.stringify(this.user));

        return { success: true, user: this.user };
      } else {
        return { success: false, error: data.message || "Login failed" };
      }
    } catch (error) {
      console.error("Login error:", error);
      return { success: false, error: "Network error" };
    }
  }

  /**
   * Register new user
   */
  async register(userData) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        return { success: true, message: data.message };
      } else {
        return { success: false, error: data.message || "Registration failed" };
      }
    } catch (error) {
      console.error("Registration error:", error);
      return { success: false, error: "Network error" };
    }
  }

  /**
   * Logout user
   */
  async logout() {
    try {
      if (this.token) {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${this.token}`,
            "Content-Type": "application/json",
          },
        });
      }
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      // Clear local data regardless of API call result
      this.token = null;
      this.user = null;
      localStorage.removeItem("auth_token");
      localStorage.removeItem("auth_user");
    }
  }

  /**
   * Get current user info
   */
  async getCurrentUser() {
    if (!this.token) return null;

    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${this.token}`,
        },
      });

      const data = await response.json();

      if (response.ok && data.success) {
        this.user = data.data;
        localStorage.setItem("auth_user", JSON.stringify(this.user));
        return this.user;
      } else {
        // Token invalid, clear auth data
        this.logout();
        return null;
      }
    } catch (error) {
      console.error("Get current user error:", error);
      return null;
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.token && !!this.user;
  }

  /**
   * Get current user
   */
  getUser() {
    return this.user;
  }

  /**
   * Get auth token
   */
  getToken() {
    return this.token;
  }

  /**
   * Check if user has specific role
   */
  hasRole(role) {
    return this.user?.role === role;
  }

  /**
   * Check if user is admin
   */
  isAdmin() {
    return this.hasRole("admin");
  }

  /**
   * Make authenticated API call
   */
  async authenticatedFetch(url, options = {}) {
    const token = this.getToken();

    if (!token) {
      throw new Error("No authentication token available");
    }

    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    // If unauthorized, clear auth data
    if (response.status === 401) {
      this.logout();
      throw new Error("Authentication failed");
    }

    return response;
  }
}

// Create and export singleton instance
const authService = new AuthService();
export default authService;
