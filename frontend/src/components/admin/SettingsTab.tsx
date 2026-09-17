import React, { useEffect, useState } from "react";
import { ProviderStatus } from "../../types";
import { api } from "../../services/api";
import { Sliders, CheckCircle2, AlertCircle, ShieldCheck, Key } from "lucide-react";

export const SettingsTab: React.FC = () => {
  const [status, setStatus] = useState<ProviderStatus | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.getProviderStatus()
      .then(setStatus)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex-1 overflow-y-auto bg-[#09090b] p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="pb-6 border-b border-zinc-800">
          <h1 className="text-xl font-semibold text-white tracking-tight">AI Provider & System Configuration</h1>
          <p className="text-xs text-zinc-400 mt-1">
            Environment provider toggle status per Part 5 specification.
          </p>
        </div>

        {status && (
          <div className="p-6 rounded-xl border border-zinc-800 bg-[#0e0e11] space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-mono uppercase text-zinc-500">Active AI Provider</span>
                <div className="text-lg font-bold text-white font-mono uppercase mt-0.5">
                  {status.provider}
                </div>
              </div>
              <span className={`px-3 py-1 rounded text-xs font-semibold uppercase font-mono border ${
                status.configured
                  ? "bg-emerald-950/40 text-emerald-300 border-emerald-800"
                  : "bg-amber-950/40 text-amber-300 border-amber-800"
              }`}>
                {status.configured ? "Key Configured" : "Local Emulation Mode"}
              </span>
            </div>

            <div className="space-y-3 pt-4 border-t border-zinc-800/80 text-xs">
              <div className="flex items-center justify-between py-2 border-b border-zinc-800/40">
                <span className="text-zinc-400">Target Model</span>
                <span className="font-mono text-white">{status.model}</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-zinc-800/40">
                <span className="text-zinc-400">API Key Privacy</span>
                <span className="font-mono text-emerald-400 flex items-center gap-1">
                  <ShieldCheck size={14} /> Never sent to frontend
                </span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-zinc-400">Environment File</span>
                <span className="font-mono text-zinc-300">.env</span>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs text-zinc-400 leading-relaxed">
              <div className="font-semibold text-zinc-200 mb-1 flex items-center gap-1.5">
                <Key size={14} /> Provider Toggle Instructions
              </div>
              To switch providers between OpenAI and xAI Grok, set <code className="text-zinc-200 bg-black/40 px-1 py-0.5 rounded">AI_PROVIDER=grok</code> or <code className="text-zinc-200 bg-black/40 px-1 py-0.5 rounded">AI_PROVIDER=openai</code> in your root <code className="text-zinc-200 bg-black/40 px-1 py-0.5 rounded">.env</code> file. No code changes are required.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

