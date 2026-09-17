import React, { useEffect, useState } from "react";
import { DemoAccount } from "../../types";
import { api } from "../../services/api";
import { X, Key, ShieldCheck, Building2 } from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSelectAccount: (username: string, password: string) => void;
}

export const DemoAccountsModal: React.FC<Props> = ({ isOpen, onClose, onSelectAccount }) => {
  const [accounts, setAccounts] = useState<DemoAccount[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      api.getDemoAccounts()
        .then(setAccounts)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="bg-[#121215] border border-zinc-800 rounded-xl w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
          <div>
            <h2 className="text-lg font-medium text-white tracking-tight">Pre-Configured Demo Accounts</h2>
            <p className="text-xs text-zinc-400 mt-0.5">Select an account to auto-populate credentials.</p>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-white p-1 rounded-md hover:bg-zinc-800 transition"
          >
            <X size={18} />
          </button>
        </div>

        <div className="p-6 overflow-y-auto space-y-3">
          {loading ? (
            <div className="text-center py-8 text-sm text-zinc-500">Loading accounts...</div>
          ) : (
            accounts.map((acc) => (
              <div
                key={acc.username}
                className="group border border-zinc-800/80 bg-zinc-900/40 hover:bg-zinc-900/80 hover:border-zinc-700 p-4 rounded-lg transition flex flex-col justify-between cursor-pointer"
                onClick={() => {
                  onSelectAccount(acc.username, acc.password_hint);
                  onClose();
                }}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-white text-sm">{acc.title}</span>
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
                        {acc.role}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-1 text-xs text-zinc-400">
                      <Building2 size={12} />
                      <span>{acc.company_name}</span>
                      <span className="text-zinc-600">•</span>
                      <span className="font-mono text-zinc-300">{acc.username}</span>
                    </div>
                  </div>
                  <button className="text-xs px-3 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 font-medium transition">
                    Use Account
                  </button>
                </div>
                <p className="text-xs text-zinc-400 mt-2.5 leading-relaxed bg-black/20 p-2 rounded border border-zinc-800/50">
                  {acc.access_description}
                </p>
              </div>
            ))
          )}
        </div>

        <div className="px-6 py-3 border-t border-zinc-800 bg-zinc-950 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs text-zinc-300 hover:text-white bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

