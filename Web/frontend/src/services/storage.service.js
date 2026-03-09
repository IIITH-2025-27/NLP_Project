import { STORAGE_KEYS } from "../utils/constants";

/**
 * LocalStorage service for managing persistent data
 */
class StorageService {
  /**
   * Get token from localStorage
   */
  getToken() {
    return localStorage.getItem(STORAGE_KEYS.TOKEN);
  }

  /**
   * Set token in localStorage
   */
  setToken(token) {
    localStorage.setItem(STORAGE_KEYS.TOKEN, token);
  }

  /**
   * Remove token from localStorage
   */
  removeToken() {
    localStorage.removeItem(STORAGE_KEYS.TOKEN);
  }

  /**
   * Get user from localStorage
   */
  getUser() {
    const user = localStorage.getItem(STORAGE_KEYS.USER);
    return user ? JSON.parse(user) : null;
  }

  /**
   * Set user in localStorage
   */
  setUser(user) {
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
  }

  /**
   * Remove user from localStorage
   */
  removeUser() {
    localStorage.removeItem(STORAGE_KEYS.USER);
  }

  /**
   * Clear all auth data
   */
  clearAuth() {
    this.removeToken();
    this.removeUser();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.getToken();
  }
}

export default new StorageService();
