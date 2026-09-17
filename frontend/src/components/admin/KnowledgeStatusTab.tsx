import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { api } from "../../services/api";
import { Database, ShieldCheck, HardDrive, Layers, Server, CheckCircle2 } from "lucide-react";

export const KnowledgeStatusTab: React.FC = () => {
  const { activeCompany } = useAuth();
  const [docCount, setDocCount] = useState(0);
  const [chunkCount, setChunkCount] = useState(0);

  useEffect(() => {
    if (activeCompany) {
      api.listDocuments(activeCompany.id).then((docs) => {
        setDocCount(docs.length);
        const total = docs.reduce((acc, d) => acc + (d.chunk_count || 0), 0);
        setChunkCount(total);
      }).catch(console.error);
    }
  }, [activeCompany]);

  return (
    <div className="flex-1 overflow-y-auto bg-[#09090b] p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-xl font-semibold text-white tracking-tight">Knowledge Base Architecture & Status</h1>
          <p className="text-xs text-zinc-400 mt-1">
            Active tenant vector partitioning, embedding model, and index metrics for{" "}
            <span className="text-zinc-200 font-medium">{activeCompany?.name}</span>.
          </p>
        </div>

        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-5 rounded-xl border border-zinc-800 bg-[#0e0e11]">
            <div className="flex items-center justify-between text-zinc-400 mb-2">
              <span className="text-xs font-mono uppercase">Indexed Documents</span>
              <HardDrive size={16} />
            </div>
            <div className="text-2xl font-semibold text-white font-mono">{docCount}</div>
            <div className="text-[11px] text-zinc-500 mt-1">Authorized in tenant scope</div>
          </div>

          <div className="p-5 rounded-xl border border-zinc-800 bg-[#0e0e11]">
            <div className="flex items-center justify-between text-zinc-400 mb-2">
              <span className="text-xs font-mono uppercase">Vector Chunks</span>
              <Layers size={16} />
            </div>
            <div className="text-2xl font-semibold text-white font-mono">{chunkCount}</div>
            <div className="text-[11px] text-zinc-500 mt-1">HNSW ANN Indexed vectors</div>
          </div>

          <div className="p-5 rounded-xl border border-zinc-800 bg-[#0e0e11]">
            <div className="flex items-center justify-between text-zinc-400 mb-2">
              <span className="text-xs font-mono uppercase">Tenant Isolation</span>
              <ShieldCheck size={16} className="text-emerald-400" />
            </div>
            <div className="text-sm font-semibold text-emerald-400 flex items-center gap-1.5 mt-2">
              <CheckCircle2 size={16} /> Strict Backend Filter
            </div>
            <div className="text-[11px] text-zinc-500 mt-1">Zero cross-company vector leakage</div>
          </div>
        </div>

        {/* Index Specifications */}
        <div className="p-6 rounded-xl border border-zinc-800 bg-[#0e0e11] space-y-4">
          <h3 className="text-sm font-semibold text-white tracking-tight flex items-center gap-2">
            <Server size={16} className="text-zinc-400" />
            Vector Store & Embedding Specifications
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-3.5 rounded-lg border border-zinc-800/80 bg-zinc-900/30">
              <div className="text-zinc-500 font-mono text-[10px] uppercase">Embedding Model</div>
              <div className="text-white font-medium mt-1 font-mono">sentence-transformers/all-MiniLM-L6-v2</div>
              <div className="text-zinc-400 mt-1 text-[11px]">384-dimensional unit-normalized dense vectors</div>
            </div>

            <div className="p-3.5 rounded-lg border border-zinc-800/80 bg-zinc-900/30">
              <div className="text-zinc-500 font-mono text-[10px] uppercase">ANN Retrieval Algorithm</div>
              <div className="text-white font-medium mt-1 font-mono">HNSW / Cosine Similarity (Top K = 40)</div>
              <div className="text-zinc-400 mt-1 text-[11px]">Sub-millisecond approximate nearest neighbor candidate search</div>
            </div>

            <div className="p-3.5 rounded-lg border border-zinc-800/80 bg-zinc-900/30">
              <div className="text-zinc-500 font-mono text-[10px] uppercase">Reranking Model</div>
              <div className="text-white font-medium mt-1 font-mono">XGBoost Relevance Classifier (Top K = 8)</div>
              <div className="text-zinc-400 mt-1 text-[11px]">Trained on 10 lexical, metadata, and version features</div>
            </div>

            <div className="p-3.5 rounded-lg border border-zinc-800/80 bg-zinc-900/30">
              <div className="text-zinc-500 font-mono text-[10px] uppercase">Security Boundary</div>
              <div className="text-white font-medium mt-1 font-mono">TenantKnowledgeStore Facade</div>
              <div className="text-zinc-400 mt-1 text-[11px]">Pre-retrieval role + department + confidentiality enforcement</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

