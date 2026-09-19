export interface Company {
  id: string;
  name: string;
  slug: string;
  description?: string;
  status: string;
  created_at: string;
  document_count?: number;
  chunk_count?: number;
}

export interface User {
  id: string;
  username: string;
  display_name: string;
  role: string;
  status: string;
  permissions: string[];
  companies: Company[];
  active_company_id?: string;
}

export interface DemoAccount {
  title: string;
  username: string;
  role: string;
  company_name: string;
  access_description: string;
  password_hint: string;
}

export interface Citation {
  id: string;
  document_id: string;
  title: string;
  page?: number;
  section?: string;
  version?: string;
  effective_date?: string;
  confidentiality?: string;
  department?: string;
  relevance_score?: number;
}

export interface EvidenceChunk {
  chunk_id: string;
  document_id: string;
  title: string;
  text: string;
  page?: number;
  section?: string;
  version?: string;
  effective_date?: string;
  department?: string;
  similarity_score: number;
  rerank_score: number;
}

export interface AgentStep {
  step: number;
  action: string;
  tool_name?: string;
  tool_args?: Record<string, any>;
  observation_summary?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  evidence?: EvidenceChunk[];
  agent_steps?: AgentStep[];
  insufficient_evidence?: boolean;
  latency_ms?: number;
  trace_id?: string;
  timestamp: string;
}

export interface DocumentItem {
  id: string;
  company_id: string;
  title: string;
  filename: string;
  document_type: string;
  department: string;
  version: string;
  effective_date?: string;
  status: string;
  confidentiality: string;
  source?: string;
  storage_path?: string;
  has_file?: boolean;
  created_at: string;
  chunk_count?: number;
}

export interface ChunkItem {
  id: string;
  document_id: string;
  company_id: string;
  chunk_index: number;
  text: string;
  page?: number;
  section?: string;
}

export interface Span {
  span_id: string;
  trace_id: string;
  name: string;
  start_time: string;
  end_time: string;
  duration_ms: number;
  status: string;
  attributes: Record<string, any>;
}

export interface Trace {
  trace_id: string;
  timestamp: string;
  company_id?: string;
  user_id?: string;
  query: string;
  total_duration_ms: number;
  status: string;
  spans: Span[];
}

export interface PlatformMetrics {
  request_count: number;
  error_count: number;
  p95_latency_ms: number;
  avg_latency_ms: number;
  avg_retrieval_latency_ms: number;
  avg_reranking_latency_ms: number;
  avg_llm_latency_ms: number;
  total_tool_calls: number;
  cache_hit_rate: number;
}

export interface EvaluationResult {
  id: string;
  question: string;
  hit_at_5: number;
  hit_at_10: number;
  hit_at_20: number;
  groundedness_score: number;
  latency_ms: number;
  generated_answer?: string;
  citations?: any[];
}

export interface EvaluationRun {
  id: string;
  tenant_id: string;
  name: string;
  status: string;
  provider: string;
  model: string;
  total_questions: number;
  recall_at_5: number;
  recall_at_10: number;
  recall_at_20: number;
  groundedness_score: number;
  avg_latency_ms: number;
  reranker_lift: number;
  created_at: string;
  results?: EvaluationResult[];
}

export interface ProviderStatus {
  provider: string;
  configured: boolean;
  model: string;
  error?: string;
}
