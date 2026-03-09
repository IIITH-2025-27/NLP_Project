import { useAuth } from "../../context/AuthContext";
import "./Header.css";

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="app-header">
      <div className="header-container">
        <div className="header-brand">
          <span className="brand-icon">𝄞</span>
          <span className="brand-text">LyricMind</span>
        </div>
        
        <div className="header-user">
          <div className="user-info">
            <span className="user-avatar">{user?.name?.charAt(0).toUpperCase() || "U"}</span>
            <span className="user-name">{user?.name}</span>
          </div>
          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
