import React from "react";
import { ChatMessage as ChatMessageType, Citation } from "../../types";
import { CitationPill } from "./CitationPill";
import { AgentStepsViewer } from "./AgentStepsViewer";
import { AlertCircle, Bot, User as UserIcon, BookOpen, Clock } from "lucide-react";

interface Props {
  message: ChatMessageType;
  onSelectCitation: (chunkId: string) => void;
  onOpenEvidence: () => void;
}

export const ChatMessage: React.FC<Props> = ({ message, onSelectCitation, onOpenEvidence }) => {
  const isUser = message.role === "user";

  return (
    <div className={`py-6 border-b border-zinc-800/60 ${isUser ? "bg-transparent" : "bg-zinc-900/10"}`}>
      <div className="max-w-4xl mx-auto px-6 flex gap-4">
        <div
          className={`w-7 h-7 rounded-md flex items-center justify-center shrink-0 border ${
            isUser
              ? "bg-zinc-800 text-zinc-300 border-zinc-700"
              : "bg-white text-black border-white"
          }`}
        >
          {isUser ? <UserIcon size={14} /> : <Bot size={15} />}
        </div>

        <div className="flex-1 space-y-3 overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-zinc-400">
              {isUser ? "You" : "Veritas Research Assistant"}
            </span>
            {message.latency_ms && (
              <span className="text-[10px] text-zinc-500 flex items-center gap-1 font-mono">
                <Clock size={10} /> {message.latency_ms.toFixed(0)}ms
              </span>
            )}
          </div>

          {/* Agent Steps if available */}
          {message.agent_steps && message.agent_steps.length > 0 && (
            <AgentStepsViewer steps={message.agent_steps} />
          )}

          {/* Insufficient Evidence Warning Banner */}
          {message.insufficient_evidence && (
            <div className="flex items-center gap-2 p-3 rounded-lg border border-amber-500/20 bg-amber-500/5 text-amber-200 text-xs">
              <AlertCircle size={15} className="shrink-0 text-amber-400" />
              <span>
                Insufficient verified evidence found in enterprise documentation to answer this query with full confidence.
              </span>
            </div>
          )}

          {/* Message Content */}
          <div className="text-sm text-zinc-200 leading-relaxed whitespace-pre-wrap font-sans">
            {message.content}
          </div>

          {/* Citations Footer */}
          {message.citations && message.citations.length > 0 && (
            <div className="pt-2 border-t border-zinc-800/40">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-medium text-zinc-400 flex items-center gap-1.5">
                  <BookOpen size={12} />
                  Cited Sources ({message.citations.length})
                </span>
                <button
                  onClick={onOpenEvidence}
                  className="text-[11px] text-zinc-400 hover:text-white underline underline-offset-2 transition"
                >
                  View All Evidence
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {message.citations.map((cite, i) => (
                  <CitationPill key={cite.id || i} citation={cite} onClick={onSelectCitation} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

