import React from "react";
import { useAuth } from "../../context/AuthContext";
import {
  MessageSquare,
  Plus,
  Files,
  Database,
  Users,
  Activity,
  BarChart3,
  Building2,
  LogOut,
  Sliders,
  ChevronDown
} from "lucide-react";

interface Props {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onNewResearch: () => void;
  onOpenCompanySwitcher: () => void;
}

export const Sidebar: React.FC<Props> = ({
  activeTab,
  setActiveTab,
  onNewResearch,
  onOpenCompanySwitcher
}) => {
  const { user, activeCompany, logout } = useAuth();
  const isPlatformAdmin = user?.role === "PLATFORM_ADMIN";
  const isCompanyAdmin = user?.role === "COMPANY_ADMIN";

  const navItems = [
    { id: "research", label: "Research Workspace", icon: MessageSquare },
    { id: "documents", label: "Documents & Ingest", icon: Files },
    { id: "knowledge", label: "Knowledge Base", icon: Database },
  ];

  const adminItems = [
    { id: "users", label: "Users & RBAC", icon: Users, permission: "user.read" },
    { id: "observability", label: "Observability & Traces", icon: Activity, permission: "observability.read" },
    { id: "evaluation", label: "Evaluation Benchmarks", icon: BarChart3, permission: "evaluation.read" },
    { id: "settings", label: "Provider Status", icon: Sliders, permission: "company.read" }
  ];

  return (
    <aside className="w-64 border-r border-zinc-800 bg-[#0c0c0e] flex flex-col h-full shrink-0 select-none">
      {/* Veritas Brand */}
      <div className="px-5 py-4 border-b border-zinc-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded bg-white flex items-center justify-center text-black font-bold text-xs tracking-tighter">
            V
          </div>
          <span className="font-semibold text-sm tracking-tight text-white">VERITAS</span>
        </div>
        <span className="text-[10px] font-mono text-zinc-500 uppercase px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">
          v1.0
        </span>
      </div>

      {/* Active Company Badge / Switcher */}
      <div className="px-3 pt-3">
        <button
          onClick={isPlatformAdmin ? onOpenCompanySwitcher : undefined}
          disabled={!isPlatformAdmin}
          className={`w-full text-left px-3 py-2 rounded-lg border flex items-center justify-between transition ${
            isPlatformAdmin
              ? "bg-zinc-900/60 hover:bg-zinc-800/80 border-zinc-800 hover:border-zinc-700 cursor-pointer"
              : "bg-zinc-900/30 border-zinc-800/60 cursor-default"
          }`}
        >
          <div className="flex items-center gap-2 overflow-hidden">
            <Building2 size={14} className="text-zinc-400 shrink-0" />
            <div className="truncate">
              <div className="text-[10px] uppercase font-mono text-zinc-500 tracking-wider leading-none">
                Active Tenant
              </div>
              <div className="text-xs font-medium text-zinc-200 truncate mt-0.5">
                {activeCompany?.name || "Loading..."}
              </div>
            </div>
          </div>
          {isPlatformAdmin && <ChevronDown size={14} className="text-zinc-500 shrink-0" />}
        </button>
      </div>

      {/* New Research Action */}
      <div className="px-3 py-3">
        <button
          onClick={onNewResearch}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 text-xs font-semibold shadow transition"
        >
          <Plus size={14} />
          New Research
        </button>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 px-3 space-y-1 overflow-y-auto">
        <div className="text-[10px] uppercase font-mono text-zinc-500 px-3 py-1 font-semibold">
          Platform
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
                isActive
                  ? "bg-zinc-800 text-white border border-zinc-700/60"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
              }`}
            >
              <Icon size={14} />
              {item.label}
            </button>
          );
        })}

        <div className="text-[10px] uppercase font-mono text-zinc-500 px-3 pt-4 py-1 font-semibold">
          Operations & Control
        </div>
        {adminItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          const hasPerm = isPlatformAdmin || user?.permissions?.includes(item.permission);
          if (!hasPerm) return null;

          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
                isActive
                  ? "bg-zinc-800 text-white border border-zinc-700/60"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
              }`}
            >
              <Icon size={14} />
              {item.label}
            </button>
          );
        })}
      </div>

      {/* User Profile Footer */}
      <div className="p-3 border-t border-zinc-800 bg-[#09090b]">
        <div className="flex items-center justify-between p-2 rounded-lg bg-zinc-900/50 border border-zinc-800/80">
          <div className="truncate">
            <div className="text-xs font-medium text-zinc-200 truncate">
              {user?.display_name || user?.username}
            </div>
            <div className="text-[10px] font-mono text-zinc-500 uppercase">
              {user?.role}
            </div>
          </div>
          <button
            onClick={logout}
            className="text-zinc-400 hover:text-white p-1.5 rounded hover:bg-zinc-800 transition"
            title="Sign out"
          >
            <LogOut size={14} />
          </button>
        </div>
      </div>
    </aside>
  );
};

