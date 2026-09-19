import {
  User,
  Company,
  DemoAccount,
  DocumentItem,
  ChunkItem,
  ChatMessage,
  Trace,
  PlatformMetrics,
  EvaluationRun,
  ProviderStatus
} from "../types";

const API_BASE = "/api/v1";

function getHeaders(): HeadersInit {
  const token = localStorage.getItem("veritas_token");
  const headers: HeadersInit = {
    "Content-Type": "application/json"
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  // Auth
  login: async (username: string, password: string, company_id?: string) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, company_id })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(err.detail || "Invalid credentials");
    }
    return res.json();
  },

  getMe: async (): Promise<User> => {
    const res = await fetch(`${API_BASE}/auth/me`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to load user profile");
    return res.json();
  },

  getDemoAccounts: async (): Promise<DemoAccount[]> => {
    const res = await fetch(`${API_BASE}/auth/demo-accounts`);
    if (!res.ok) throw new Error("Failed to load demo accounts");
    return res.json();
  },

  // Companies
  listCompanies: async (): Promise<Company[]> => {
    const res = await fetch(`${API_BASE}/companies`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to load companies");
    return res.json();
  },

  switchCompany: async (company_id: string) => {
    const res = await fetch(`${API_BASE}/companies/switch`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ company_id })
    });
    if (!res.ok) throw new Error("Failed to switch company");
    return res.json();
  },

  // Users
  listUsers: async (): Promise<User[]> => {
    const res = await fetch(`${API_BASE}/users`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to load users");
    return res.json();
  },

  createUser: async (userData: any): Promise<User> => {
    const res = await fetch(`${API_BASE}/users`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(userData)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Create failed" }));
      throw new Error(err.detail || "Failed to create user");
    }
    return res.json();
  },

  // Documents
  listDocuments: async (companyId: string, department?: string): Promise<DocumentItem[]> => {
    let url = `${API_BASE}/documents?company_id=${companyId}`;
    if (department) url += `&department=${encodeURIComponent(department)}`;
    const res = await fetch(url, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to load documents");
    return res.json();
  },

  getDocumentChunks: async (documentId: string): Promise<ChunkItem[]> => {
    const res = await fetch(`${API_BASE}/documents/${documentId}/chunks`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to load document chunks");
    return res.json();
  },

  getDocumentFileUrl: (documentId: string, page?: number): string => {
    const token = localStorage.getItem("veritas_token");
    let url = `${API_BASE}/documents/${documentId}/file`;
    const params = new URLSearchParams();
    if (token) params.set("token", token);
    const qs = params.toString();
    if (qs) url += `?${qs}`;
    if (page && page > 0) url += `#page=${page}`;
    return url;
  },

  getDocumentFileBlob: async (documentId: string): Promise<Blob> => {
    const res = await fetch(`${API_BASE}/documents/${documentId}/file`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to load physical document file");
    return res.blob();
  },

  uploadDocument: async (formData: FormData): Promise<any> => {
    const token = localStorage.getItem("veritas_token");
    const headers: HeadersInit = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      headers,
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail || "Failed to upload document");
    }
    return res.json();
  },

  deleteDocument: async (documentId: string): Promise<any> => {
    const res = await fetch(`${API_BASE}/documents/${documentId}`, {
      method: "DELETE",
      headers: getHeaders()
    });
    if (!res.ok) throw new Error("Failed to delete document");
    return res.json();
  },

  // Chat
  sendChatQuery: async (query: string, companyId: string): Promise<any> => {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ query, company_id: companyId })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Query failed" }));
      throw new Error(err.detail || "Failed to execute query");
    }
    return res.json();
  },

  // Observability
  getTraces: async (): Promise<Trace[]> => {
    const res = await fetch(`${API_BASE}/observability/traces`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to load traces");
    return res.json();
  },

  getMetrics: async (): Promise<PlatformMetrics> => {
    const res = await fetch(`${API_BASE}/observability/metrics`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to load metrics");
    return res.json();
  },

  // Evaluation
  runEvaluation: async (companyId?: string, name?: string): Promise<EvaluationRun> => {
    const res = await fetch(`${API_BASE}/evaluation/run`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ company_id: companyId, name })
    });
    if (!res.ok) throw new Error("Failed to run benchmark evaluation");
    return res.json();
  },

  listEvaluationRuns: async (): Promise<EvaluationRun[]> => {
    const res = await fetch(`${API_BASE}/evaluation/runs`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to load evaluation runs");
    return res.json();
  },

  getEvaluationRun: async (id: string): Promise<EvaluationRun> => {
    const res = await fetch(`${API_BASE}/evaluation/runs/${id}`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to load evaluation details");
    return res.json();
  },

  // Provider
  getProviderStatus: async (): Promise<ProviderStatus> => {
    const res = await fetch(`${API_BASE}/provider/status`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to load provider status");
    return res.json();
  }
};

