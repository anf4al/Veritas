import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { EvaluationRun } from "../../types";
import { api } from "../../services/api";
import { BarChart3, Play, Loader2, ArrowUpRight, CheckCircle2, ChevronRight, Scale } from "lucide-react";

export const EvaluationTab: React.FC = () => {
  const { activeCompany } = useAuth();
  const [runs, setRuns] = useState<EvaluationRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<EvaluationRun | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  const loadRuns = async () => {
    setLoading(true);
    try {
      const data = await api.listEvaluationRuns();
      setRuns(data);
      if (data.length > 0 && !selectedRun) {
        const full = await api.getEvaluationRun(data[0].id);
        setSelectedRun(full);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRuns();
  }, []);

  const handleRunBenchmark = async () => {
    setRunning(true);
    try {
      const newRun = await api.runEvaluation(activeCompany?.id, "Full Benchmark Evaluation");
      const full = await api.getEvaluationRun(newRun.id);
      setSelectedRun(full);
      await loadRuns();
    } catch (err: any) {
      alert(`Evaluation error: ${err.message}`);
    } finally {
      setRunning(false);
    }
  };

  const handleSelectRun = async (runId: string) => {
    try {
      const full = await api.getEvaluationRun(runId);
      setSelectedRun(full);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#09090b] overflow-hidden p-8">
      <div className="flex items-center justify-between pb-6 border-b border-zinc-800">
        <div>
          <h1 className="text-xl font-semibold text-white tracking-tight">System Evaluation & Benchmarks</h1>
          <p className="text-xs text-zinc-400 mt-1">
            Empirical measurements of Recall@K, XGBoost ranking lift, groundedness, and latencies.
          </p>
        </div>
        <button
          onClick={handleRunBenchmark}
          disabled={running}
          className="flex items-center gap-2 px-4 py-2 bg-white hover:bg-zinc-200 text-black text-xs font-semibold rounded-lg shadow transition disabled:opacity-50"
        >
          {running ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
          {running ? "Evaluating 10 Seed Questions..." : "Run Benchmark"}
        </button>
      </div>

      <div className="flex-1 flex gap-6 mt-6 overflow-hidden">
        {/* Left: Runs List */}
        <div className="w-80 border border-zinc-800 rounded-xl bg-[#0e0e11] overflow-y-auto p-3 space-y-2 shrink-0">
          <div className="text-[11px] font-mono uppercase text-zinc-500 px-2 py-1 font-semibold">
            Historical Benchmark Runs ({runs.length})
          </div>
          {runs.map((r) => {
            const isSelected = selectedRun?.id === r.id;
            return (
              <div
                key={r.id}
                onClick={() => handleSelectRun(r.id)}
                className={`p-3 rounded-lg border cursor-pointer transition ${
                  isSelected
                    ? "bg-zinc-800/80 border-white/50"
                    : "bg-zinc-900/40 border-zinc-800 hover:border-zinc-700"
                }`}
              >
                <div className="font-medium text-xs text-white truncate">{r.name}</div>
                <div className="flex items-center justify-between mt-2 text-[11px] text-zinc-400 font-mono">
                  <span>Recall@5: {(r.recall_at_5 * 100).toFixed(0)}%</span>
                  <span>Lift: +{r.reranker_lift.toFixed(1)}</span>
                </div>
                <div className="text-[10px] text-zinc-500 mt-1 font-mono">
                  {new Date(r.created_at).toLocaleDateString()} • {r.avg_latency_ms.toFixed(0)}ms
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Selected Run Details */}
        <div className="flex-1 flex flex-col overflow-y-auto border border-zinc-800 rounded-xl bg-[#0e0e11] p-6 space-y-6">
          {selectedRun ? (
            <>
              <div>
                <div className="flex items-center justify-between">
                  <h2 className="text-base font-semibold text-white">{selectedRun.name}</h2>
                  <span className="text-xs font-mono text-zinc-400">
                    Provider: <strong className="text-white uppercase">{selectedRun.provider}</strong>
                  </span>
                </div>
                <p className="text-xs text-zinc-400 mt-1">
                  Tested {selectedRun.total_questions} evaluation benchmark inquiries against the enterprise dataset.
                </p>
              </div>

              {/* KPI Score Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-zinc-900/60 border border-zinc-800">
                  <div className="text-[11px] font-mono uppercase text-zinc-500">Recall @ 5</div>
                  <div className="text-2xl font-bold font-mono text-white mt-1">
                    {(selectedRun.recall_at_5 * 100).toFixed(1)}%
                  </div>
                  <div className="text-[10px] text-zinc-500 mt-1">Top-5 relevant retrieval hit</div>
                </div>

                <div className="p-4 rounded-lg bg-zinc-900/60 border border-zinc-800">
                  <div className="text-[11px] font-mono uppercase text-zinc-500">Recall @ 10 / 20</div>
                  <div className="text-2xl font-bold font-mono text-white mt-1">
                    {(selectedRun.recall_at_10 * 100).toFixed(0)}% / {(selectedRun.recall_at_20 * 100).toFixed(0)}%
                  </div>
                  <div className="text-[10px] text-zinc-500 mt-1">Expanded recall window</div>
                </div>

                <div className="p-4 rounded-lg bg-zinc-900/60 border border-zinc-800">
                  <div className="text-[11px] font-mono uppercase text-zinc-500">XGBoost Lift</div>
                  <div className="text-2xl font-bold font-mono text-emerald-400 mt-1 flex items-center gap-1">
                    +{selectedRun.reranker_lift.toFixed(1)} <ArrowUpRight size={18} />
                  </div>
                  <div className="text-[10px] text-zinc-500 mt-1">Rank elevation over ANN</div>
                </div>

                <div className="p-4 rounded-lg bg-zinc-900/60 border border-zinc-800">
                  <div className="text-[11px] font-mono uppercase text-zinc-500">Avg Latency</div>
                  <div className="text-2xl font-bold font-mono text-white mt-1">
                    {selectedRun.avg_latency_ms.toFixed(0)} ms
                  </div>
                  <div className="text-[10px] text-zinc-500 mt-1">Groundedness: {(selectedRun.groundedness_score * 100).toFixed(0)}%</div>
                </div>
              </div>

              {/* Per Question Results Table */}
              <div className="space-y-3">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono">
                  Detailed Test Item Results ({selectedRun.results?.length || 0})
                </h3>

                <div className="border border-zinc-800 rounded-lg overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-zinc-900 text-zinc-400 font-mono text-[10px] uppercase border-b border-zinc-800">
                      <tr>
                        <th className="py-2.5 px-3">Evaluation Question</th>
                        <th className="py-2.5 px-3">Hit @ 5</th>
                        <th className="py-2.5 px-3">Grounded</th>
                        <th className="py-2.5 px-3">Latency</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/60">
                      {selectedRun.results?.map((res, i) => (
                        <tr key={res.id || i} className="hover:bg-zinc-900/40 transition">
                          <td className="py-2.5 px-3 text-zinc-200 font-medium max-w-md truncate">
                            {res.question}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                              res.hit_at_5 ? "bg-emerald-950/40 text-emerald-300 border border-emerald-800" : "bg-zinc-800 text-zinc-500"
                            }`}>
                              {res.hit_at_5 ? "HIT" : "MISS"}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 font-mono text-zinc-400">
                            {(res.groundedness_score * 100).toFixed(0)}%
                          </td>
                          <td className="py-2.5 px-3 font-mono text-zinc-400">
                            {res.latency_ms.toFixed(0)}ms
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-24 text-zinc-500 text-xs">
              No evaluation run selected. Click "Run Benchmark" to execute benchmark evaluation.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

