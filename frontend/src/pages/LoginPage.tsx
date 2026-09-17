import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { DemoAccountsModal } from "../components/demo/DemoAccountsModal";
import { Eye, EyeOff, Loader2, Sparkles, Shield, Key } from "lucide-react";

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
    } catch (err: any) {
      setError(err.message || "Invalid username or password.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDemoAccount = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
    setError(null);
  };

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-[#09090b] text-white p-4 select-none relative">
      <div className="w-full max-w-sm space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="w-10 h-10 rounded-xl bg-white text-black flex items-center justify-center font-bold text-base mx-auto shadow-md">
            V
          </div>
          <h1 className="text-xl font-semibold tracking-tight text-white">VERITAS</h1>
          <p className="text-xs text-zinc-400">Enterprise Intelligence & Research Platform</p>
        </div>

        {/* Login Form Card */}
        <div className="p-6 rounded-2xl border border-zinc-800/80 bg-[#101014] shadow-2xl space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-900 text-rose-300 text-xs leading-relaxed">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1.5">
                Username or Email
              </label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. admin@veritas.demo"
                className="w-full px-3.5 py-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 transition"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full px-3.5 py-2.5 pr-10 rounded-lg bg-zinc-900/80 border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 transition"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-zinc-400 hover:text-zinc-200 transition"
                >
                  {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-lg bg-white text-zinc-950 text-xs font-semibold hover:bg-zinc-200 disabled:opacity-50 transition shadow mt-2 flex items-center justify-center gap-2"
            >
              {loading && <Loader2 size={14} className="animate-spin" />}
              {loading ? "Authenticating..." : "Sign In"}
            </button>
          </form>

          {/* Quick Demo Helper Trigger */}
          <div className="pt-2 text-center border-t border-zinc-800/60">
            <button
              type="button"
              onClick={() => setIsDemoModalOpen(true)}
              className="text-xs text-zinc-400 hover:text-white underline underline-offset-2 transition inline-flex items-center gap-1.5"
            >
              <Key size={12} />
              View Pre-Configured Demo Accounts
            </button>
          </div>
        </div>

        {/* Footer info */}
        <div className="text-center text-[11px] text-zinc-600 space-y-1">
          <div>Multi-Tenant Enterprise RAG • Zero-Trust Knowledge Isolation</div>
          <div className="font-mono text-[10px] text-zinc-700">Veritas v1.0.0</div>
        </div>
      </div>

      {/* Demo Accounts Modal */}
      <DemoAccountsModal
        isOpen={isDemoModalOpen}
        onClose={() => setIsDemoModalOpen(false)}
        onSelectAccount={handleSelectDemoAccount}
      />
    </div>
  );
};

