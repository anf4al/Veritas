import React, { useState } from "react";
import { Citation, EvidenceChunk } from "../../types";
import { PdfViewerModal } from "../documents/PdfViewerModal";
import { X, FileText, Calendar, Hash, Shield, Layers, Award, ExternalLink } from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  citations: Citation[];
  evidence: EvidenceChunk[];
  activeChunkId?: string;
}

interface PdfTarget {
  documentId: string;
  title: string;
  page: number;
  department?: string;
  version?: string;
  effective_date?: string;
}

export const EvidenceDrawer: React.FC<Props> = ({
  isOpen,
  onClose,
  citations,
  evidence,
  activeChunkId
}) => {
  const [viewingPdf, setViewingPdf] = useState<PdfTarget | null>(null);

  if (!isOpen) return null;

  return (
    <>
      <aside className="w-96 border-l border-zinc-800 bg-[#0c0c0e] flex flex-col h-full z-20 shrink-0">
        <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800">
          <div>
            <h3 className="text-sm font-semibold text-white tracking-tight flex items-center gap-2">
              <Award size={16} className="text-zinc-400" />
              Verified Evidence & Citations
            </h3>
            <p className="text-[11px] text-zinc-400 mt-0.5">
              {evidence.length} chunks retrieved & reranked via XGBoost
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-white p-1 rounded hover:bg-zinc-800 transition"
          >
            <X size={16} />
          </button>
        </div>

        <div className="p-4 overflow-y-auto space-y-4 flex-1">
          {evidence.length === 0 ? (
            <div className="text-center py-12 text-zinc-500 text-xs">
              No evidence chunks available for this request.
            </div>
          ) : (
            evidence.map((chunk, idx) => {
              const isTarget = activeChunkId && chunk.chunk_id === activeChunkId;
              return (
                <div
                  key={chunk.chunk_id || idx}
                  id={`evidence-${chunk.chunk_id}`}
                  className={`p-3.5 rounded-lg border transition ${
                    isTarget
                      ? "bg-zinc-800/80 border-white/40 ring-1 ring-white/20"
                      : "bg-zinc-900/40 border-zinc-800 hover:border-zinc-700"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-medium text-xs text-white leading-tight">
                      {chunk.title}
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700 shrink-0">
                      Rerank: {(chunk.rerank_score * 100).toFixed(0)}%
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 mt-2 text-[10px] text-zinc-400">
                    <span className="flex items-center gap-1 bg-black/30 px-1.5 py-0.5 rounded border border-zinc-800">
                      <FileText size={10} /> p.{chunk.page || 1}
                    </span>
                    {chunk.section && (
                      <span className="flex items-center gap-1 bg-black/30 px-1.5 py-0.5 rounded border border-zinc-800">
                        <Layers size={10} /> {chunk.section}
                      </span>
                    )}
                    {chunk.version && (
                      <span className="flex items-center gap-1 bg-black/30 px-1.5 py-0.5 rounded border border-zinc-800">
                        v{chunk.version}
                      </span>
                    )}
                    {chunk.effective_date && (
                      <span className="flex items-center gap-1 bg-black/30 px-1.5 py-0.5 rounded border border-zinc-800">
                        <Calendar size={10} /> {chunk.effective_date}
                      </span>
                    )}
                  </div>

                  {/* "View in PDF" button */}
                  {chunk.document_id && (
                    <div className="mt-2.5 pt-2 border-t border-zinc-800/50 flex items-center justify-between">
                      <button
                        onClick={() => setViewingPdf({
                          documentId: chunk.document_id,
                          title: chunk.title,
                          page: chunk.page || 1,
                          department: chunk.department,
                          version: chunk.version,
                          effective_date: chunk.effective_date
                        })}
                        className="flex items-center gap-1.5 text-[10px] text-blue-400 hover:text-blue-300 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/20 px-2 py-0.5 rounded transition"
                        title="Open PDF navigated to this cited page"
                      >
                        <ExternalLink size={10} />
                        View in PDF (Page {chunk.page || 1})
                      </button>
                    </div>
                  )}

                  <div className="mt-2 text-xs text-zinc-300 leading-relaxed font-sans bg-black/30 p-2 rounded border border-zinc-800/60 whitespace-pre-wrap">
                    {chunk.text}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </aside>

      {/* Embedded PDF Viewer Modal for Evidence */}
      {viewingPdf && (
        <PdfViewerModal
          isOpen={!!viewingPdf}
          onClose={() => setViewingPdf(null)}
          documentId={viewingPdf.documentId}
          title={viewingPdf.title}
          initialPage={viewingPdf.page}
          metadata={{
            department: viewingPdf.department,
            version: viewingPdf.version,
            effective_date: viewingPdf.effective_date
          }}
        />
      )}
    </>
  );
};
