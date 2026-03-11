import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import authService from "../services/auth.service";
import Input from "../components/common/Input";
import Button from "../components/common/Button";
import ErrorMessage from "../components/common/ErrorMessage";
import "../assets/styles/auth.css";
import girlWithMusic from "../assets/girl_with_music.mp4";

export default function AuthPage() {
  const { login } = useAuth();
  const [mode, setMode] = useState("login"); // login | signup | verify-otp
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [resendTimer, setResendTimer] = useState(0);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const startResendTimer = () => {
    setResendTimer(60);
    const interval = setInterval(() => {
      setResendTimer((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleRequestOTP = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!form.name || !form.email || !form.password) {
      return setError("Please fill all fields.");
    }

    if (form.password.length < 6) {
      return setError("Password must be at least 6 characters.");
    }

    setLoading(true);
    try {
      await authService.requestOTP(form.name, form.email, form.password);
      setSuccess("OTP sent to your email! Please check your inbox.");
      setOtpSent(true);
      setMode("verify-otp");
      startResendTimer();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!otp || otp.length !== 6) {
      return setError("Please enter a valid 6-digit OTP.");
    }

    setLoading(true);
    try {
      const response = await authService.verifyOTP(form.email, otp);
      setSuccess("Signup successful! Welcome to LyricMind.");
      login(response.user, response.token);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    if (resendTimer > 0) return;
    
    setError("");
    setSuccess("");
    setLoading(true);
    
    try {
      await authService.resendOTP(form.email);
      setSuccess("OTP resent successfully! Please check your email.");
      startResendTimer();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    if (!form.email || !form.password) {
      return setError("Please fill all fields.");
    }

    setLoading(true);
    try {
      const response = await authService.login(form.email, form.password);
      login(response.user, response.token);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const switchToLogin = () => {
    setMode("login");
    setError("");
    setSuccess("");
    setOtpSent(false);
    setOtp("");
    setForm({ name: "", email: "", password: "" });
  };

  const switchToSignup = () => {
    setMode("signup");
    setError("");
    setSuccess("");
    setOtpSent(false);
    setOtp("");
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
          <div className="video-container">
            <video 
              src={girlWithMusic} 
              className="auth-video" 
              autoPlay 
              loop 
              muted 
              playsInline
            />
            <div className="video-overlay">
              <div className="brand-logo">𝄞</div>
              <h1 className="brand-title">LyricMind</h1>
              <p className="brand-tagline">Your emotions. Your verse.</p>
            </div>
          </div>
        </div>

        <div className="auth-right">
          <div className="welcome-header">
            <div className="brand-logo-small">𝄞</div>
            <h1 className="welcome-title">Welcome to LyricMind!</h1>
          </div>
          <div className="auth-card">
            {mode !== "verify-otp" && (
              <div className="auth-tabs">
                <button
                  className={`auth-tab ${mode === "login" ? "active" : ""}`}
                  onClick={switchToLogin}
                >
                  Sign In
                </button>
                <button
                  className={`auth-tab ${mode === "signup" ? "active" : ""}`}
                  onClick={switchToSignup}
                >
                  Sign Up
                </button>
              </div>
            )}

            <div className="auth-form-container">
              {mode === "verify-otp" ? (
                <>
                  <h2 className="auth-form-title">Verify Your Email</h2>
                  <p className="auth-form-subtitle">
                    We've sent a 6-digit code to {form.email}
                  </p>

                  {error && <ErrorMessage message={error} onClose={() => setError("")} />}
                  {success && (
                    <div style={{
                      padding: "12px",
                      background: "rgba(34, 197, 94, 0.1)",
                      border: "1px solid rgba(34, 197, 94, 0.3)",
                      borderRadius: "8px",
                      color: "#22c55e",
                      marginBottom: "20px",
                      fontSize: "14px"
                    }}>
                      {success}
                    </div>
                  )}

                  <form onSubmit={handleVerifyOTP} className="auth-form">
                    <div style={{ marginBottom: "20px" }}>
                      <label style={{
                        display: "block",
                        marginBottom: "8px",
                        fontSize: "14px",
                        fontWeight: "500",
                        color: "#e2e8f0"
                      }}>
                        Enter OTP
                      </label>
                      <input
                        type="text"
                        value={otp}
                        onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                        placeholder="000000"
                        maxLength="6"
                        style={{
                          width: "100%",
                          padding: "14px 16px",
                          fontSize: "20px",
                          letterSpacing: "8px",
                          textAlign: "center",
                          background: "rgba(255, 255, 255, 0.05)",
                          border: "2px solid rgba(255, 255, 255, 0.1)",
                          borderRadius: "12px",
                          color: "#fff",
                          fontWeight: "600",
                          transition: "all 0.3s ease",
                          outline: "none"
                        }}
                        onFocus={(e) => e.target.style.borderColor = "#a78bfa"}
                        onBlur={(e) => e.target.style.borderColor = "rgba(255, 255, 255, 0.1)"}
                      />
                    </div>

                    <Button type="submit" fullWidth loading={loading}>
                      Verify & Sign Up
                    </Button>

                    <div style={{
                      marginTop: "20px",
                      textAlign: "center",
                      fontSize: "14px",
                      color: "#94a3b8"
                    }}>
                      Didn't receive the code?{" "}
                      {resendTimer > 0 ? (
                        <span style={{ color: "#64748b" }}>
                          Resend in {resendTimer}s
                        </span>
                      ) : (
                        <button
                          type="button"
                          onClick={handleResendOTP}
                          disabled={loading}
                          style={{
                            background: "none",
                            border: "none",
                            color: "#a78bfa",
                            cursor: "pointer",
                            textDecoration: "underline",
                            padding: 0,
                            font: "inherit"
                          }}
                        >
                          Resend OTP
                        </button>
                      )}
                    </div>

                    <button
                      type="button"
                      onClick={switchToLogin}
                      style={{
                        marginTop: "15px",
                        width: "100%",
                        padding: "10px",
                        background: "none",
                        border: "1px solid rgba(255, 255, 255, 0.1)",
                        borderRadius: "8px",
                        color: "#94a3b8",
                        cursor: "pointer",
                        fontSize: "14px",
                        transition: "all 0.3s ease"
                      }}
                      onMouseOver={(e) => {
                        e.target.style.borderColor = "rgba(255, 255, 255, 0.3)";
                        e.target.style.color = "#e2e8f0";
                      }}
                      onMouseOut={(e) => {
                        e.target.style.borderColor = "rgba(255, 255, 255, 0.1)";
                        e.target.style.color = "#94a3b8";
                      }}
                    >
                      Back to Login
                    </button>
                  </form>
                </>
              ) : (
                <>
                  <h2 className="auth-form-title">
                    {mode === "login" ? "Welcome back" : "Create account"}
                  </h2>
                  <p className="auth-form-subtitle">
                    {mode === "login"
                      ? "Continue your creative journey"
                      : "Start turning emotions into art"}
                  </p>

                  {error && <ErrorMessage message={error} onClose={() => setError("")} />}
                  {success && (
                    <div style={{
                      padding: "12px",
                      background: "rgba(34, 197, 94, 0.1)",
                      border: "1px solid rgba(34, 197, 94, 0.3)",
                      borderRadius: "8px",
                      color: "#22c55e",
                      marginBottom: "20px",
                      fontSize: "14px"
                    }}>
                      {success}
                    </div>
                  )}

                  <form 
                    onSubmit={mode === "login" ? handleLogin : handleRequestOTP} 
                    className="auth-form"
                  >
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
                      {mode === "login" ? "Sign In" : "Send OTP"}
                    </Button>
                  </form>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
