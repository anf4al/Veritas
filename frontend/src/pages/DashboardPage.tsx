import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Sidebar } from "../components/layout/Sidebar";
import { ChatWorkspace } from "../components/chat/ChatWorkspace";
import { DocumentsTab } from "../components/admin/DocumentsTab";
import { KnowledgeStatusTab } from "../components/admin/KnowledgeStatusTab";
import { UsersTab } from "../components/admin/UsersTab";
import { ObservabilityTab } from "../components/admin/ObservabilityTab";
import { EvaluationTab } from "../components/admin/EvaluationTab";
import { SettingsTab } from "../components/admin/SettingsTab";
import { CompanySwitcher } from "../components/admin/CompanySwitcher";

export const DashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("research");
  const [isCompanySwitcherOpen, setIsCompanySwitcherOpen] = useState(false);

  return (
    <div className="flex h-screen w-screen bg-[#09090b] text-white overflow-hidden">
      {/* Left Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onNewResearch={() => setActiveTab("research")}
        onOpenCompanySwitcher={() => setIsCompanySwitcherOpen(true)}
      />

      {/* Main View Area */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-[#09090b]">
        {activeTab === "research" && <ChatWorkspace />}
        {activeTab === "documents" && <DocumentsTab />}
        {activeTab === "knowledge" && <KnowledgeStatusTab />}
        {activeTab === "users" && <UsersTab />}
        {activeTab === "observability" && <ObservabilityTab />}
        {activeTab === "evaluation" && <EvaluationTab />}
        {activeTab === "settings" && <SettingsTab />}
      </main>

      {/* Company Switcher Modal */}
      <CompanySwitcher
        isOpen={isCompanySwitcherOpen}
        onClose={() => setIsCompanySwitcherOpen(false)}
      />
    </div>
  );
};

