import React, { useEffect, useState } from "react";
import { Company } from "../../types";
import { api } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { X, Building2, Check, FileText, Database } from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export const CompanySwitcher: React.FC<Props> = ({ isOpen, onClose }) => {
  const { activeCompany, switchActiveCompany } = useAuth();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      api.listCompanies()
        .then(setCompanies)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="bg-[#121215] border border-zinc-800 rounded-xl w-full max-w-lg shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
          <div>
            <h2 className="text-sm font-semibold text-white tracking-tight">Switch Active Company</h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Switch the active knowledge base workspace (Platform Admin).
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-white p-1 rounded hover:bg-zinc-800 transition"
          >
            <X size={16} />
          </button>
        </div>

        <div className="p-6 space-y-3">
          {loading ? (
            <div className="text-center py-6 text-xs text-zinc-500">Loading companies...</div>
          ) : (
            companies.map((c) => {
              const isSelected = activeCompany?.id === c.id;
              return (
                <div
                  key={c.id}
                  onClick={async () => {
                    await switchActiveCompany(c.id);
                    onClose();
                  }}
                  className={`p-4 rounded-lg border cursor-pointer transition flex items-center justify-between ${
                    isSelected
                      ? "bg-zinc-800/80 border-white/50 ring-1 ring-white/20"
                      : "bg-zinc-900/40 border-zinc-800 hover:border-zinc-700 hover:bg-zinc-900"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded bg-zinc-800 border border-zinc-700 text-zinc-300 mt-0.5">
                      <Building2 size={16} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm text-white">{c.name}</span>
                        {isSelected && (
                          <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-white text-black font-semibold">
                            Active
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-zinc-400 mt-1 line-clamp-1">{c.description}</p>
                      <div className="flex items-center gap-3 mt-2 text-[11px] text-zinc-500 font-mono">
                        <span className="flex items-center gap-1">
                          <FileText size={11} /> {c.document_count || 0} docs
                        </span>
                        <span className="flex items-center gap-1">
                          <Database size={11} /> {c.chunk_count || 0} chunks
                        </span>
                      </div>
                    </div>
                  </div>

                  {isSelected && <Check size={18} className="text-white" />}
                </div>
              );
            })
          )}
        </div>

        <div className="px-6 py-3 border-t border-zinc-800 bg-zinc-950 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs text-zinc-300 hover:text-white bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded transition"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

