import React, { useState, useEffect } from "react";
import { api } from "../../services/api";
import {
  X,
  ChevronLeft,
  ChevronRight,
  Download,
  ExternalLink,
  FileText,
  Shield,
  Layers,
  Calendar,
  AlertCircle,
  Loader2
} from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
  title: string;
  initialPage?: number;
  metadata?: {
    department?: string;
    version?: string;
    confidentiality?: string;
    effective_date?: string;
    document_type?: string;
  };
}

export const PdfViewerModal: React.FC<Props> = ({
  isOpen,
  onClose,
  documentId,
  title,
  initialPage = 1,
  metadata
}) => {
  const [currentPage, setCurrentPage] = useState<number>(initialPage);
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setCurrentPage(initialPage);
  }, [initialPage]);

  useEffect(() => {
    if (!isOpen || !documentId) {
      if (blobUrl) {
        URL.revokeObjectURL(blobUrl);
        setBlobUrl(null);
      }
      return;
    }

    let active = true;
    setLoading(true);
    setError(null);

    api.getDocumentFileBlob(documentId)
      .then((blob) => {
        if (!active) return;
        const url = URL.createObjectURL(blob);
        setBlobUrl(url);
        setLoading(false);
      })
      .catch((err) => {
        if (!active) return;
        console.error("Failed to load PDF:", err);
        setError(err.message || "Unable to load document file.");
        setLoading(false);
      });

    return () => {
      active = false;
      if (blobUrl) {
        URL.revokeObjectURL(blobUrl);
      }
    };
  }, [isOpen, documentId]);

  if (!isOpen) return null;

  const handlePrevPage = () => {
    setCurrentPage((prev) => Math.max(1, prev - 1));
  };

  const handleNextPage = () => {
    setCurrentPage((prev) => prev + 1);
  };

  const fileViewerUrl = blobUrl ? `${blobUrl}#page=${currentPage}` : "";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 sm:p-6 animate-in fade-in duration-150">
      <div className="bg-[#111114] border border-zinc-800 rounded-xl w-full max-w-5xl h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header Bar */}
        <div className="flex items-center justify-between px-6 py-3.5 border-b border-zinc-800 bg-[#0c0c0e]">
          <div className="flex items-center gap-3 min-w-0">
            <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 shrink-0">
              <FileText size={18} />
            </div>
            <div className="min-w-0">
              <h3 className="text-sm font-semibold text-white truncate tracking-tight">
                {title}
              </h3>
              <div className="flex items-center gap-2 mt-0.5 text-[11px] text-zinc-400 flex-wrap">
                {metadata?.department && (
                  <span className="flex items-center gap-1">
                    <Layers size={11} className="text-zinc-500" /> {metadata.department}
                  </span>
                )}
                {metadata?.version && (
                  <span className="px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-300 font-mono text-[10px]">
                    v{metadata.version}
                  </span>
                )}
                {metadata?.confidentiality && (
                  <span className="flex items-center gap-1 uppercase tracking-wider text-[10px] text-amber-400/90 font-medium">
                    <Shield size={10} /> {metadata.confidentiality}
                  </span>
                )}
                {metadata?.effective_date && (
                  <span className="flex items-center gap-1 text-zinc-500">
                    <Calendar size={11} /> {metadata.effective_date}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Navigation and Action Controls */}
          <div className="flex items-center gap-3">
            {/* Page Navigator */}
            <div className="flex items-center gap-1 bg-zinc-900 border border-zinc-800 rounded-lg px-2 py-1">
              <button
                onClick={handlePrevPage}
                disabled={currentPage <= 1 || loading}
                title="Previous page"
                className="p-1 rounded text-zinc-400 hover:text-white hover:bg-zinc-800 disabled:opacity-40 disabled:hover:bg-transparent"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="text-xs font-mono text-zinc-300 px-1.5">
                Page {currentPage}
              </span>
              <button
                onClick={handleNextPage}
                disabled={loading}
                title="Next page"
                className="p-1 rounded text-zinc-400 hover:text-white hover:bg-zinc-800 disabled:opacity-40"
              >
                <ChevronRight size={16} />
              </button>
            </div>

            {/* Direct File Actions */}
            {blobUrl && (
              <a
                href={blobUrl}
                download={`${title.replace(/\s+/g, "_")}.pdf`}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition"
                title="Download PDF"
              >
                <Download size={16} />
              </a>
            )}
            {blobUrl && (
              <a
                href={blobUrl}
                target="_blank"
                rel="noreferrer"
                className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition"
                title="Open in new tab"
              >
                <ExternalLink size={16} />
              </a>
            )}

            <div className="h-4 w-px bg-zinc-800 mx-1" />

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition"
              title="Close viewer"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Document Viewer Frame / Loading State */}
        <div className="flex-1 relative bg-zinc-950 flex items-center justify-center overflow-hidden">
          {loading && (
            <div className="flex flex-col items-center gap-3 text-zinc-400">
              <Loader2 size={32} className="animate-spin text-blue-500" />
              <p className="text-xs font-medium tracking-wide">Streaming verified PDF document...</p>
            </div>
          )}

          {error && !loading && (
            <div className="flex flex-col items-center gap-3 max-w-md text-center p-6 bg-red-950/20 border border-red-900/40 rounded-xl text-zinc-300">
              <AlertCircle size={28} className="text-red-400" />
              <h4 className="text-sm font-semibold text-white">Document File Unavailable</h4>
              <p className="text-xs text-zinc-400 leading-relaxed">{error}</p>
              <button
                onClick={onClose}
                className="mt-2 px-4 py-1.5 text-xs rounded-lg bg-zinc-800 hover:bg-zinc-700 text-white transition"
              >
                Close Viewer
              </button>
            </div>
          )}

          {!loading && !error && blobUrl && (
            <iframe
              key={`${documentId}-${currentPage}`}
              src={fileViewerUrl}
              className="w-full h-full border-0 bg-zinc-900"
              title={title}
            />
          )}
        </div>
      </div>
    </div>
  );
};

