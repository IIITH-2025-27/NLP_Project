import apiService from "./api.service";
import storageService from "./storage.service";

/**
 * Authentication service
 */
class AuthService {
  /**
   * Request OTP for signup
   */
  async requestOTP(name, email, password) {
    return await apiService.requestOTP(name, email, password);
  }

  /**
   * Verify OTP and complete signup
   */
  async verifyOTP(email, otp) {
    const response = await apiService.verifyOTP(email, otp);
    if (response.token && response.user) {
      storageService.setToken(response.token);
      storageService.setUser(response.user);
    }
    return response;
  }

  /**
   * Resend OTP
   */
  async resendOTP(email) {
    return await apiService.resendOTP(email);
  }

  /**
   * Sign up new user (legacy - without OTP)
   */
  async signup(name, email, password) {
    const response = await apiService.signup(name, email, password);
    if (response.token && response.user) {
      storageService.setToken(response.token);
      storageService.setUser(response.user);
    }
    return response;
  }

  /**
   * Login user
   */
  async login(email, password) {
    const response = await apiService.login(email, password);
    if (response.token && response.user) {
      storageService.setToken(response.token);
      storageService.setUser(response.user);
    }
    return response;
  }

  /**
   * Logout user
   */
  logout() {
    storageService.clearAuth();
  }

  /**
   * Get current user
   */
  getCurrentUser() {
    return storageService.getUser();
  }

  /**
   * Get current token
   */
  getToken() {
    return storageService.getToken();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return storageService.isAuthenticated();
  }
}

export default new AuthService();
