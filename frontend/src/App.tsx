import React from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { Loader2 } from "lucide-react";

const AppContent: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen w-screen flex flex-col items-center justify-center bg-[#09090b] text-white gap-3">
        <Loader2 size={24} className="animate-spin text-zinc-400" />
        <span className="text-xs font-mono text-zinc-500 tracking-wider uppercase">Loading Veritas...</span>
      </div>
    );
  }

  return user ? <DashboardPage /> : <LoginPage />;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;

