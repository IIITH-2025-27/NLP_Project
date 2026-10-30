import { API_BASE_URL } from "../utils/constants";
import storageService from "./storage.service";

/**
 * Extract error message from error detail (handles both string and object)
 */
const extractErrorMessage = (detail) => {
  if (typeof detail === 'string') {
    return detail;
  }
  if (typeof detail === 'object' && detail !== null) {
    // Try different error message fields
    return detail.error || detail.message || detail.detail || JSON.stringify(detail);
  }
  return 'Request failed';
};

export const SESSION_EXPIRED_EVENT = "lyricmind:session-expired";

/**
 * A 401 on an authenticated, non-auth call means the token expired or is invalid.
 * (Auth endpoints return 401 for wrong passwords, so they are excluded.)
 */
const checkSessionExpired = (response, endpoint, token) => {
  if (response.status === 401 && token && !endpoint.startsWith("/auth/")) {
    window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
  }
};

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

    checkSessionExpired(response, endpoint, token);
    const data = await response.json();

    if (!response.ok) {
      const errorMessage = extractErrorMessage(data.detail);
      throw new Error(errorMessage);
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

  forgotPassword: (email) =>
    request("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),

  verifyResetOTP: (email, otp) =>
    request("/auth/verify-reset-otp", {
      method: "POST",
      body: JSON.stringify({ email, otp }),
    }),

  resetPassword: (email, otp, new_password) =>
    request("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({ email, otp, new_password }),
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

      checkSessionExpired(response, "/getEmotionFromImage", token);
      const data = await response.json();

      if (!response.ok) {
        const errorMessage = extractErrorMessage(data.detail);
        throw new Error(errorMessage);
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

  // PHREM quality score for generated lyrics (slow, so fetched after lyrics are shown)
  evaluateLyrics: (lyrics, emotion, recordId) =>
    request("/evaluateLyrics", {
      method: "POST",
      body: JSON.stringify({ lyrics, emotion, record_id: recordId }),
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

  updateMessage: (messageId, messageData) =>
    request(`/messages/${messageId}`, {
      method: "PUT",
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
