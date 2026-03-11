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

  requestOTP: (name, email, password) =>
    request("/auth/request-otp", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    }),

  verifyOTP: (email, otp) =>
    request("/auth/verify-otp", {
      method: "POST",
      body: JSON.stringify({ email, otp }),
    }),

  resendOTP: (email) =>
    request("/auth/resend-otp", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),

  login: (email, password) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  // ML/AI endpoints
  
  // Get emotion from text
  getEmotionFromText: (text) =>
    request("/getEmotionFromText", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),

  // Get emotion from image
  getEmotionFromImage: async (imageFile) => {
    const url = `${API_BASE_URL}/getEmotionFromImage`;
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

  // Get lyrics for emotion
  getLyricsForEmotion: (emotion) =>
    request("/getLyricsForEmotion", {
      method: "POST",
      body: JSON.stringify({ emotion }),
    }),

  // Legacy analyze endpoint (calls getEmotionFromText)
  analyze: (text) =>
    request("/getEmotionFromText", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),

  // Legacy analyzeImage endpoint (calls getEmotionFromImage)
  analyzeImage: async (imageFile) => {
    return apiService.getEmotionFromImage(imageFile);
  },

  // Chat endpoints
  getChats: () => request("/chats"),

  getChat: (chatId) => request(`/chats/${chatId}`),

  createChat: (title = "New Chat") =>
    request("/chats", {
      method: "POST",
      body: JSON.stringify({ title }),
    }),

  updateChat: (chatId, data) =>
    request(`/chats/${chatId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  deleteChat: (chatId) =>
    request(`/chats/${chatId}`, {
      method: "DELETE",
    }),

  // Message endpoints
  getMessages: (chatId) => request(`/chats/${chatId}/messages`),

  createMessage: (chatId, messageData) =>
    request(`/chats/${chatId}/messages`, {
      method: "POST",
      body: JSON.stringify(messageData),
    }),

  deleteMessage: (messageId) =>
    request(`/messages/${messageId}`, {
      method: "DELETE",
    }),

  // Health check
  healthCheck: () => request("/"),
};

export default apiService;
