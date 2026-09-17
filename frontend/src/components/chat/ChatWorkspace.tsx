import React, { useState, useRef, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { ChatMessage as ChatMessageType, Citation, EvidenceChunk } from "../../types";
import { api } from "../../services/api";
import { ChatMessage } from "./ChatMessage";
import { EvidenceDrawer } from "../layout/EvidenceDrawer";
import {
  Send,
  Loader2,
  Sparkles,
  HelpCircle,
  FileCheck,
  ShieldAlert,
  ArrowRight
} from "lucide-react";

export const ChatWorkspace: React.FC = () => {
  const { activeCompany, user } = useAuth();
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // Evidence Drawer state
  const [isEvidenceOpen, setIsEvidenceOpen] = useState(false);
  const [activeEvidence, setActiveEvidence] = useState<EvidenceChunk[]>([]);
  const [activeCitations, setActiveCitations] = useState<Citation[]>([]);
  const [selectedChunkId, setSelectedChunkId] = useState<string | undefined>(undefined);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const samplePrompts = [
    "What is the current WFH policy?",
    "How many annual leave days can an employee carry forward?",
    "What changed between the 2025 and 2026 procurement policies?",
    "Why was Vendor Atlas classified as high risk, and does our contract allow termination?",
    "Which contracts expire within 90 days?"
  ];

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || !activeCompany || loading) return;

    const userMessage: ChatMessageType = {
      id: `usr-${Date.now()}`,
      role: "user",
      content: textToSend.trim(),
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const resp = await api.sendChatQuery(textToSend.trim(), activeCompany.id);

      const assistantMessage: ChatMessageType = {
        id: `asst-${Date.now()}`,
        role: "assistant",
        content: resp.answer,
        citations: resp.citations || [],
        evidence: resp.evidence || [],
        agent_steps: resp.agent_steps || [],
        insufficient_evidence: resp.insufficient_evidence,
        latency_ms: resp.latency_ms,
        trace_id: resp.trace_id,
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setActiveEvidence(resp.evidence || []);
      setActiveCitations(resp.citations || []);
      if (resp.evidence && resp.evidence.length > 0) {
        setIsEvidenceOpen(true);
      }
    } catch (err: any) {
      const errorMessage: ChatMessageType = {
        id: `err-${Date.now()}`,
        role: "assistant",
        content: `Error executing research query: ${err.message || "Unknown error"}`,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCitation = (chunkId: string) => {
    setSelectedChunkId(chunkId);
    setIsEvidenceOpen(true);
  };

  return (
    <div className="flex-1 flex h-full overflow-hidden relative">
      <div className="flex-1 flex flex-col h-full bg-[#09090b]">
        {/* Messages Feed */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="max-w-3xl mx-auto px-6 py-16 text-center">
              <div className="w-12 h-12 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mx-auto mb-4 text-white shadow-lg">
                <Sparkles size={22} className="text-zinc-300" />
              </div>
              <h2 className="text-xl font-semibold text-white tracking-tight">
                Veritas Enterprise Intelligence
              </h2>
              <p className="text-xs text-zinc-400 max-w-md mx-auto mt-1.5 leading-relaxed">
                Query {activeCompany?.name}'s private knowledge base with multi-tenant RBAC,
                XGBoost reranking, and verified source citations.
              </p>

              {/* Sample Prompt Cards */}
              <div className="mt-8 text-left">
                <div className="text-[11px] font-mono uppercase text-zinc-500 mb-3 font-semibold">
                  Example Research Inquiries
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                  {samplePrompts.map((p, i) => (
                    <button
                      key={i}
                      onClick={() => handleSend(p)}
                      className="text-left p-3.5 rounded-lg border border-zinc-800/80 bg-zinc-900/30 hover:bg-zinc-900 hover:border-zinc-700 transition flex items-center justify-between group"
                    >
                      <span className="text-xs text-zinc-300 group-hover:text-white font-medium pr-2">
                        {p}
                      </span>
                      <ArrowRight size={14} className="text-zinc-600 group-hover:text-zinc-300 shrink-0 transition" />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-zinc-800/40 pb-6">
              {messages.map((m) => (
                <ChatMessage
                  key={m.id}
                  message={m}
                  onSelectCitation={handleSelectCitation}
                  onOpenEvidence={() => {
                    if (m.evidence) setActiveEvidence(m.evidence);
                    if (m.citations) setActiveCitations(m.citations);
                    setIsEvidenceOpen(true);
                  }}
                />
              ))}

              {loading && (
                <div className="py-6 px-6 max-w-4xl mx-auto flex items-center gap-3 text-xs text-zinc-400">
                  <Loader2 size={16} className="animate-spin text-zinc-300" />
                  <span>Retrieving authorized evidence, reranking with XGBoost & synthesizing answer...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-zinc-800/80 bg-[#09090b]">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="max-w-4xl mx-auto relative flex items-center"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Ask a question over ${activeCompany?.name || "company"} records...`}
              disabled={loading}
              className="w-full py-3.5 pl-4 pr-12 rounded-xl bg-zinc-900/70 border border-zinc-800 focus:border-zinc-600 focus:outline-none focus:ring-1 focus:ring-zinc-600 text-sm text-white placeholder-zinc-500 transition shadow-inner"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="absolute right-2.5 p-2 rounded-lg bg-white text-black hover:bg-zinc-200 disabled:opacity-30 disabled:hover:bg-white transition"
            >
              {loading ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
            </button>
          </form>
          <div className="max-w-4xl mx-auto mt-2 flex items-center justify-between text-[11px] text-zinc-500">
            <span>Documents are treated as untrusted data. Responses are cited against authorized company records.</span>
            <span>Role: <strong className="text-zinc-400 uppercase font-mono">{user?.role}</strong></span>
          </div>
        </div>
      </div>

      {/* Slide-out Evidence Drawer */}
      <EvidenceDrawer
        isOpen={isEvidenceOpen}
        onClose={() => setIsEvidenceOpen(false)}
        citations={activeCitations}
        evidence={activeEvidence}
        activeChunkId={selectedChunkId}
      />
    </div>
  );
};

