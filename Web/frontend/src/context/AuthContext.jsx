import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("lyricmind_token"));
  const [loading, setLoading] = useState(true);

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
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
