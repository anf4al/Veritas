import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { DocumentItem, ChunkItem } from "../../types";
import { api } from "../../services/api";
import {
  Upload,
  FileText,
  Trash2,
  Eye,
  X,
  Search,
  CheckCircle2,
  Clock,
  Building2,
  Filter
} from "lucide-react";

export const DocumentsTab: React.FC = () => {
  const { activeCompany, user } = useAuth();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedDept, setSelectedDept] = useState<string>("");

  // Upload modal state
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadDept, setUploadDept] = useState("Operations");
  const [uploadType, setUploadType] = useState("policy");
  const [uploadConfidentiality, setUploadConfidentiality] = useState("internal");
  const [uploadVersion, setUploadVersion] = useState("1.0");
  const [uploading, setUploading] = useState(false);

  // Chunk inspection state
  const [inspectDoc, setInspectDoc] = useState<DocumentItem | null>(null);
  const [chunks, setChunks] = useState<ChunkItem[]>([]);
  const [loadingChunks, setLoadingChunks] = useState(false);

  const loadDocuments = async () => {
    if (!activeCompany) return;
    setLoading(true);
    try {
      const data = await api.listDocuments(activeCompany.id, selectedDept || undefined);
      setDocuments(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [activeCompany, selectedDept]);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !activeCompany) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", uploadFile);
      formData.append("company_id", activeCompany.id);
      if (uploadTitle) formData.append("title", uploadTitle);
      formData.append("department", uploadDept);
      formData.append("document_type", uploadType);
      formData.append("confidentiality", uploadConfidentiality);
      formData.append("version", uploadVersion);

      await api.uploadDocument(formData);
      setIsUploadOpen(false);
      setUploadFile(null);
      setUploadTitle("");
      await loadDocuments();
    } catch (err: any) {
      alert(`Upload error: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleInspectChunks = async (doc: DocumentItem) => {
    setInspectDoc(doc);
    setLoadingChunks(true);
    try {
      const c = await api.getDocumentChunks(doc.id);
      setChunks(c);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingChunks(false);
    }
  };

  const handleDelete = async (docId: string, title: string) => {
    if (!confirm(`Are you sure you want to delete '${title}'?`)) return;
    try {
      await api.deleteDocument(docId);
      await loadDocuments();
    } catch (err: any) {
      alert(`Delete error: ${err.message}`);
    }
  };

  const filteredDocs = documents.filter((d) =>
    d.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.department.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.document_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const departments = Array.from(new Set(documents.map((d) => d.department))).sort();

  return (
    <div className="flex-1 flex flex-col h-full bg-[#09090b] overflow-hidden p-8">
      {/* Header */}
      <div className="flex items-center justify-between pb-6 border-b border-zinc-800">
        <div>
          <h1 className="text-xl font-semibold text-white tracking-tight">Enterprise Knowledge Documents</h1>
          <p className="text-xs text-zinc-400 mt-1">
            Browse, inspect, and ingest documents for <span className="text-zinc-200">{activeCompany?.name}</span>.
          </p>
        </div>
        <button
          onClick={() => setIsUploadOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-white hover:bg-zinc-200 text-black text-xs font-semibold rounded-lg shadow transition"
        >
          <Upload size={14} />
          Upload Document
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex items-center gap-4 my-6">
        <div className="relative flex-1 max-w-md">
          <Search size={14} className="absolute left-3.5 top-3 text-zinc-500" />
          <input
            type="text"
            placeholder="Search by title, department, or type..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-600"
          />
        </div>

        <div className="flex items-center gap-2 text-xs text-zinc-400">
          <Filter size={14} />
          <select
            value={selectedDept}
            onChange={(e) => setSelectedDept(e.target.value)}
            className="bg-zinc-900 border border-zinc-800 text-xs text-white rounded-lg px-3 py-2 focus:outline-none"
          >
            <option value="">All Departments</option>
            {departments.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        <div className="text-xs text-zinc-500 font-mono ml-auto">
          Showing {filteredDocs.length} of {documents.length} docs
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-y-auto border border-zinc-800 rounded-xl bg-[#0e0e11]">
        <table className="w-full text-left text-xs">
          <thead className="bg-zinc-900/80 text-zinc-400 font-mono text-[11px] uppercase border-b border-zinc-800 sticky top-0">
            <tr>
              <th className="py-3 px-4">Title</th>
              <th className="py-3 px-4">Department</th>
              <th className="py-3 px-4">Type</th>
              <th className="py-3 px-4">Version</th>
              <th className="py-3 px-4">Confidentiality</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Chunks</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {loading ? (
              <tr>
                <td colSpan={8} className="text-center py-12 text-zinc-500">
                  Loading documents...
                </td>
              </tr>
            ) : filteredDocs.length === 0 ? (
              <tr>
                <td colSpan={8} className="text-center py-12 text-zinc-500">
                  No documents found matching filters.
                </td>
              </tr>
            ) : (
              filteredDocs.map((doc) => (
                <tr key={doc.id} className="hover:bg-zinc-900/40 transition">
                  <td className="py-3 px-4 font-medium text-white flex items-center gap-2">
                    <FileText size={14} className="text-zinc-400 shrink-0" />
                    <span className="truncate max-w-xs">{doc.title}</span>
                  </td>
                  <td className="py-3 px-4 text-zinc-300">{doc.department}</td>
                  <td className="py-3 px-4 text-zinc-400 uppercase font-mono text-[10px]">{doc.document_type}</td>
                  <td className="py-3 px-4 font-mono text-zinc-400">v{doc.version}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-mono border ${
                      doc.confidentiality === "restricted"
                        ? "bg-rose-950/40 border-rose-800 text-rose-300"
                        : doc.confidentiality === "confidential"
                        ? "bg-amber-950/40 border-amber-800 text-amber-300"
                        : "bg-zinc-900 border-zinc-800 text-zinc-400"
                    }`}>
                      {doc.confidentiality}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400">
                      <CheckCircle2 size={12} /> {doc.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-zinc-400">{doc.chunk_count || "-"}</td>
                  <td className="py-3 px-4 text-right space-x-2">
                    <button
                      onClick={() => handleInspectChunks(doc)}
                      className="p-1 hover:bg-zinc-800 text-zinc-400 hover:text-white rounded transition"
                      title="Inspect Chunks"
                    >
                      <Eye size={14} />
                    </button>
                    <button
                      onClick={() => handleDelete(doc.id, doc.title)}
                      className="p-1 hover:bg-rose-950 text-zinc-500 hover:text-rose-400 rounded transition"
                      title="Delete Document"
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Upload Modal */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="bg-[#121215] border border-zinc-800 rounded-xl w-full max-w-lg shadow-2xl overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
              <h3 className="text-sm font-semibold text-white">Upload and Ingest Document</h3>
              <button onClick={() => setIsUploadOpen(false)} className="text-zinc-400 hover:text-white">
                <X size={16} />
              </button>
            </div>
            <form onSubmit={handleUpload} className="p-6 space-y-4 text-xs">
              <div>
                <label className="block text-zinc-400 mb-1">Select File (.txt, .md, .pdf, .docx)</label>
                <input
                  type="file"
                  required
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="w-full text-zinc-300 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-zinc-800 file:text-white hover:file:bg-zinc-700 cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-zinc-400 mb-1">Document Title (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Master Service Level Agreement 2026"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  className="w-full p-2.5 rounded bg-zinc-900 border border-zinc-800 text-white focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-zinc-400 mb-1">Department</label>
                  <input
                    type="text"
                    value={uploadDept}
                    onChange={(e) => setUploadDept(e.target.value)}
                    className="w-full p-2.5 rounded bg-zinc-900 border border-zinc-800 text-white focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-zinc-400 mb-1">Document Type</label>
                  <select
                    value={uploadType}
                    onChange={(e) => setUploadType(e.target.value)}
                    className="w-full p-2.5 rounded bg-zinc-900 border border-zinc-800 text-white focus:outline-none"
                  >
                    <option value="policy">Policy</option>
                    <option value="contract">Contract</option>
                    <option value="report">Report</option>
                    <option value="sop">SOP</option>
                    <option value="manual">Manual</option>
                    <option value="handbook">Handbook</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-zinc-400 mb-1">Confidentiality</label>
                  <select
                    value={uploadConfidentiality}
                    onChange={(e) => setUploadConfidentiality(e.target.value)}
                    className="w-full p-2.5 rounded bg-zinc-900 border border-zinc-800 text-white focus:outline-none"
                  >
                    <option value="public">Public</option>
                    <option value="internal">Internal</option>
                    <option value="confidential">Confidential</option>
                    <option value="restricted">Restricted</option>
                  </select>
                </div>
                <div>
                  <label className="block text-zinc-400 mb-1">Version</label>
                  <input
                    type="text"
                    value={uploadVersion}
                    onChange={(e) => setUploadVersion(e.target.value)}
                    className="w-full p-2.5 rounded bg-zinc-900 border border-zinc-800 text-white focus:outline-none"
                  />
                </div>
              </div>

              <div className="pt-3 flex justify-end gap-2 border-t border-zinc-800">
                <button
                  type="button"
                  onClick={() => setIsUploadOpen(false)}
                  className="px-4 py-2 rounded bg-zinc-900 text-zinc-300 hover:text-white border border-zinc-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading || !uploadFile}
                  className="px-4 py-2 rounded bg-white text-black font-semibold hover:bg-zinc-200 disabled:opacity-50"
                >
                  {uploading ? "Ingesting & Chunking..." : "Ingest & Index"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Chunk Inspection Modal */}
      {inspectDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="bg-[#121215] border border-zinc-800 rounded-xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
              <div>
                <h3 className="text-sm font-semibold text-white truncate max-w-md">{inspectDoc.title}</h3>
                <p className="text-xs text-zinc-400">
                  {chunks.length} chunks indexed in vector store
                </p>
              </div>
              <button onClick={() => setInspectDoc(null)} className="text-zinc-400 hover:text-white">
                <X size={16} />
              </button>
            </div>
            <div className="p-6 overflow-y-auto space-y-3">
              {loadingChunks ? (
                <div className="text-center py-12 text-zinc-500 text-xs">Loading chunks...</div>
              ) : chunks.map((c) => (
                <div key={c.id} className="p-3 rounded-lg border border-zinc-800 bg-zinc-900/40 text-xs">
                  <div className="flex items-center justify-between text-[11px] font-mono text-zinc-400 mb-1.5">
                    <span>Chunk #{c.chunk_index + 1} (Page {c.page || 1})</span>
                    <span>{c.section || "General"}</span>
                  </div>
                  <p className="text-zinc-300 whitespace-pre-wrap leading-relaxed">{c.text}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

