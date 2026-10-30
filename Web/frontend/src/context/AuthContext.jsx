import { createContext, useContext, useState, useEffect } from "react";
import { SESSION_EXPIRED_EVENT } from "../services/api.service";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("lyricmind_token"));
  const [loading, setLoading] = useState(true);
  const [sessionExpired, setSessionExpired] = useState(false);

  // The API layer fires this on a 401; drop the stale session so the login page shows.
  useEffect(() => {
    const onExpired = () => {
      localStorage.removeItem("lyricmind_token");
      localStorage.removeItem("lyricmind_user");
      setToken(null);
      setUser(null);
      setSessionExpired(true);
    };
    window.addEventListener(SESSION_EXPIRED_EVENT, onExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, onExpired);
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem("lyricmind_user");
    const savedToken = localStorage.getItem("lyricmind_token");
    if (saved && savedToken) {
      const userData = JSON.parse(saved);
      setUser(userData);
      setToken(savedToken);
    }
    setLoading(false);
  }, []);

  const login =(userData, authToken) => {
    setSessionExpired(false);
    setUser(userData);
    setToken(authToken);
    localStorage.setItem("lyricmind_token", authToken);
    localStorage.setItem("lyricmind_user", JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("lyricmind_token");
    localStorage.removeItem("lyricmind_user");
    window.location.reload(); // Reload to clear all state
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading, sessionExpired }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
