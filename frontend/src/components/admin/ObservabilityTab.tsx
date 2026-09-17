import React, { useEffect, useState } from "react";
import { Trace, PlatformMetrics } from "../../types";
import { api } from "../../services/api";
import { Activity, Clock, Zap, AlertCircle, RefreshCw, ChevronDown, ChevronRight, Layers } from "lucide-react";

export const ObservabilityTab: React.FC = () => {
  const [metrics, setMetrics] = useState<PlatformMetrics | null>(null);
  const [traces, setTraces] = useState<Trace[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedTraceId, setExpandedTraceId] = useState<string | null>(null);

  const loadTelemetry = async () => {
    setLoading(true);
    try {
      const [m, t] = await Promise.all([api.getMetrics(), api.getTraces()]);
      setMetrics(m);
      setTraces(t);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTelemetry();
  }, []);

  return (
    <div className="flex-1 overflow-y-auto bg-[#09090b] p-8 space-y-8">
      <div className="flex items-center justify-between pb-6 border-b border-zinc-800">
        <div>
          <h1 className="text-xl font-semibold text-white tracking-tight">Observability, Telemetry & Traces</h1>
          <p className="text-xs text-zinc-400 mt-1">
            Real-time request metrics, component latency breakdowns, and end-to-end span traces.
          </p>
        </div>
        <button
          onClick={loadTelemetry}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 hover:text-white rounded-lg text-xs transition"
        >
          <RefreshCw size={13} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {/* Metric Cards */}
      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl border border-zinc-800 bg-[#0e0e11]">
            <div className="text-xs font-mono uppercase text-zinc-500">P95 Latency</div>
            <div className="text-2xl font-semibold text-white font-mono mt-1">
              {metrics.p95_latency_ms.toFixed(0)} ms
            </div>
            <div className="text-[11px] text-zinc-500 mt-1">Avg: {metrics.avg_latency_ms.toFixed(0)} ms</div>
          </div>

          <div className="p-4 rounded-xl border border-zinc-800 bg-[#0e0e11]">
            <div className="text-xs font-mono uppercase text-zinc-500">Retrieval & Rerank</div>
            <div className="text-2xl font-semibold text-white font-mono mt-1">
              {(metrics.avg_retrieval_latency_ms + metrics.avg_reranking_latency_ms).toFixed(0)} ms
            </div>
            <div className="text-[11px] text-zinc-500 mt-1">
              ANN: {metrics.avg_retrieval_latency_ms.toFixed(0)}ms | XGB: {metrics.avg_reranking_latency_ms.toFixed(0)}ms
            </div>
          </div>

          <div className="p-4 rounded-xl border border-zinc-800 bg-[#0e0e11]">
            <div className="text-xs font-mono uppercase text-zinc-500">Total Tool Invocations</div>
            <div className="text-2xl font-semibold text-white font-mono mt-1">
              {metrics.total_tool_calls}
            </div>
            <div className="text-[11px] text-zinc-500 mt-1">Agent multi-step calls</div>
          </div>

          <div className="p-4 rounded-xl border border-zinc-800 bg-[#0e0e11]">
            <div className="text-xs font-mono uppercase text-zinc-500">Total Requests</div>
            <div className="text-2xl font-semibold text-white font-mono mt-1">
              {metrics.request_count}
            </div>
            <div className="text-[11px] text-zinc-500 mt-1">Errors: {metrics.error_count}</div>
          </div>
        </div>
      )}

      {/* Traces Timeline */}
      <div className="space-y-4">
        <h2 className="text-sm font-semibold text-white tracking-tight flex items-center gap-2">
          <Activity size={16} className="text-zinc-400" />
          Recent Request Traces ({traces.length})
        </h2>

        <div className="border border-zinc-800 rounded-xl bg-[#0e0e11] divide-y divide-zinc-800/60 overflow-hidden">
          {traces.length === 0 ? (
            <div className="text-center py-12 text-zinc-500 text-xs">
              No traces recorded yet. Execute queries in Research Workspace to capture traces.
            </div>
          ) : (
            traces.map((trace) => {
              const isExpanded = expandedTraceId === trace.trace_id;
              return (
                <div key={trace.trace_id} className="p-4 transition hover:bg-zinc-900/20">
                  <div
                    onClick={() => setExpandedTraceId(isExpanded ? null : trace.trace_id)}
                    className="flex items-center justify-between cursor-pointer select-none"
                  >
                    <div className="flex items-center gap-3">
                      {isExpanded ? <ChevronDown size={15} className="text-zinc-400" /> : <ChevronRight size={15} className="text-zinc-400" />}
                      <div>
                        <span className="font-medium text-xs text-white line-clamp-1">{trace.query}</span>
                        <div className="flex items-center gap-2 mt-0.5 text-[10px] font-mono text-zinc-500">
                          <span>{trace.trace_id}</span>
                          <span>•</span>
                          <span>{trace.spans.length} spans</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono text-zinc-300">
                        {trace.total_duration_ms.toFixed(0)} ms
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase ${
                        trace.status === "completed"
                          ? "bg-emerald-950/40 border border-emerald-800 text-emerald-300"
                          : "bg-rose-950/40 border border-rose-800 text-rose-300"
                      }`}>
                        {trace.status}
                      </span>
                    </div>
                  </div>

                  {/* Span Breakdown */}
                  {isExpanded && (
                    <div className="mt-4 pl-6 space-y-2 border-l border-zinc-800 text-xs font-mono">
                      {trace.spans.map((s) => (
                        <div key={s.span_id} className="flex items-center justify-between p-2 rounded bg-zinc-900/50 border border-zinc-800/60">
                          <div className="flex items-center gap-2">
                            <Layers size={12} className="text-zinc-500" />
                            <span className="text-zinc-300 font-semibold">{s.name}</span>
                          </div>
                          <div className="flex items-center gap-4 text-zinc-400">
                            <span>{s.duration_ms.toFixed(1)} ms</span>
                            <span className={s.status === "ok" ? "text-emerald-400" : "text-rose-400"}>
                              {s.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

