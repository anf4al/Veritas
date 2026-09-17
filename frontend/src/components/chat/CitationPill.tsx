import React from "react";
import { Citation } from "../../types";
import { FileText } from "lucide-react";

interface Props {
  citation: Citation;
  onClick: (chunkId: string) => void;
}

export const CitationPill: React.FC<Props> = ({ citation, onClick }) => {
  return (
    <button
      onClick={() => onClick(citation.id)}
      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] bg-zinc-800/80 hover:bg-zinc-700 text-zinc-300 hover:text-white border border-zinc-700 transition"
      title={`Document: ${citation.title} | Section: ${citation.section || "General"} | v${citation.version || "1.0"}`}
    >
      <FileText size={10} className="text-zinc-400" />
      <span className="font-medium truncate max-w-[180px]">{citation.title}</span>
      <span className="text-zinc-500 font-mono">p.{citation.page || 1}</span>
    </button>
  );
};

