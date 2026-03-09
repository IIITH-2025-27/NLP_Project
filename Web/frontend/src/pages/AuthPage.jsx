import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import authService from "../services/auth.service";
import Input from "../components/common/Input";
import Button from "../components/common/Button";
import ErrorMessage from "../components/common/ErrorMessage";
import "../assets/styles/auth.css";

export default function AuthPage() {
  const { login } = useAuth();
  const [mode, setMode] = useState("login"); // login | signup
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!form.email || !form.password) {
      return setError("Please fill all fields.");
    }
    if (mode === "signup" && !form.name) {
      return setError("Name is required.");
    }

    setLoading(true);
    try {
      const response = mode === "login" 
        ? await authService.login(form.email, form.password)
        : await authService.signup(form.name, form.email, form.password);
      
      login(response.user, response.token);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-background">
        {[...Array(20)].map((_, i) => (
          <span key={i} className="auth-particle" style={{ "--i": i }} />
        ))}
      </div>

      <div className="auth-container">
        <div className="auth-left">
          <div className="auth-brand-section">
            <div className="brand-logo">𝄞</div>
            <h1 className="brand-title">LyricMind</h1>
            <p className="brand-tagline">Your emotions. Your verse.</p>
          </div>
          
          <div className="auth-features">
            <div className="feature-item">
              <span className="feature-icon">🧠</span>
              <div className="feature-content">
                <h3>Emotion Detection</h3>
                <p>Advanced NLP to understand your feelings</p>
              </div>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🎵</span>
              <div className="feature-content">
                <h3>Lyric Generation</h3>
                <p>AI-powered creative writing</p>
              </div>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📜</span>
              <div className="feature-content">
                <h3>History Tracking</h3>
                <p>Save and revisit your creations</p>
              </div>
            </div>
          </div>
        </div>

        <div className="auth-right">
          <div className="auth-card">
            <div className="auth-tabs">
              <button
                className={`auth-tab ${mode === "login" ? "active" : ""}`}
                onClick={() => { setMode("login"); setError(""); setForm({ ...form, name: "" }); }}
              >
                Sign In
              </button>
              <button
                className={`auth-tab ${mode === "signup" ? "active" : ""}`}
                onClick={() => { setMode("signup"); setError(""); }}
              >
                Sign Up
              </button>
            </div>

            <div className="auth-form-container">
              <h2 className="auth-form-title">
                {mode === "login" ? "Welcome back" : "Create account"}
              </h2>
              <p className="auth-form-subtitle">
                {mode === "login"
                  ? "Continue your creative journey"
                  : "Start turning emotions into art"}
              </p>

              {error && <ErrorMessage message={error} onClose={() => setError("")} />}

              <form onSubmit={handleSubmit} className="auth-form">
                {mode === "signup" && (
                  <Input
                    label="Full Name"
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    placeholder="Ada Lovelace"
                    icon="👤"
                  />
                )}

                <Input
                  label="Email"
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="you@example.com"
                  icon="✉️"
                />

                <Input
                  label="Password"
                  type="password"
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  icon="🔒"
                />

                <Button 
                  type="submit" 
                  fullWidth 
                  loading={loading}
                >
                  {mode === "login" ? "Sign In" : "Sign Up"}
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
