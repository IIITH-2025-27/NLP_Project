import { useEffect } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import AuthPage from "./pages/AuthPage";
import Dashboard from "./pages/Dashboard";
import Loader from "./components/common/Loader";
import { API_BASE_URL } from "./utils/constants";

function AppInner() {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '100vh' 
      }}>
        <Loader size="lg" text="Loading..." />
      </div>
    );
  }
  
  return user ? <Dashboard /> : <AuthPage />;
}

export default function App() {
  // Wake the free-tier backend while the user is still on the login screen.
  useEffect(() => {
    fetch(`${API_BASE_URL}/`).catch(() => {});
  }, []);

  return (
    <AuthProvider>
      <AppInner />
    </AuthProvider>
  );
}
