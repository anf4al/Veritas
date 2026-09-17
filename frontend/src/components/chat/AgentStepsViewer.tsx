import React, { useState } from "react";
import { AgentStep } from "../../types";
import { ChevronDown, ChevronRight, Cpu, CheckCircle2 } from "lucide-react";

interface Props {
  steps: AgentStep[];
}

export const AgentStepsViewer: React.FC<Props> = ({ steps }) => {
  const [expanded, setExpanded] = useState(false);

  if (!steps || steps.length === 0) return null;

  return (
    <div className="border border-zinc-800 rounded-lg bg-zinc-900/30 overflow-hidden text-xs my-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-3 py-2 text-zinc-400 hover:text-zinc-200 transition"
      >
        <div className="flex items-center gap-2">
          <Cpu size={14} className="text-zinc-400" />
          <span className="font-mono text-[11px] uppercase tracking-wider">
            Agent Reasoning & Multi-Step Retrieval ({steps.length} steps)
          </span>
        </div>
        {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
      </button>

      {expanded && (
        <div className="px-3 pb-3 space-y-2 border-t border-zinc-800/60 pt-2 font-mono text-[11px]">
          {steps.map((s) => (
            <div key={s.step} className="flex items-start gap-2 text-zinc-300">
              <CheckCircle2 size={12} className="text-zinc-500 mt-0.5 shrink-0" />
              <div>
                <span className="text-zinc-400 font-semibold">Step {s.step}: </span>
                <span className="text-white">{s.action} </span>
                {s.observation_summary && (
                  <div className="text-zinc-500 text-[10px] mt-0.5">{s.observation_summary}</div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

