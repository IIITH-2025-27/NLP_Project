import { API_BASE_URL } from "../utils/constants";
import storageService from "./storage.service";

/**
 * Base HTTP request handler
 */
const request = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = storageService.getToken();

  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    return data;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};

/**
 * API Service for all backend calls
 */
const apiService = {
  // Auth endpoints
  signup: (name, email, password) =>
    request("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    }),

  login: (email, password) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  // Analysis endpoint
  analyze: (text) =>
    request("/analyze", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),

  // Image analysis endpoint
  analyzeImage: async (imageFile) => {
    const url = `${API_BASE_URL}/analyze-image`;
    const token = storageService.getToken();

    const formData = new FormData();
    formData.append("image", imageFile);

    const headers = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        method: "POST",
        headers,
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Request failed");
      }

      return data;
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  },

  // History endpoints
  getHistory: () => request("/history"),

  deleteHistory: (id) =>
    request(`/history/${id}`, {
      method: "DELETE",
    }),

  // Health check
  healthCheck: () => request("/"),
};

export default apiService;
