# VERITAS — MASTER BUILD SPECIFICATION

## Purpose

Build Veritas, a production-minded enterprise intelligence and research platform. Veritas lets authenticated employees ask natural-language questions over a company's private knowledge base and receive evidence-backed answers with source citations.

This is NOT a generic chatbot and NOT an extension of GMT Marbles or ShadowTrace. Its core identity is enterprise RAG + agentic retrieval + permissions + evidence-backed generation.

The application must be runnable locally and easy to switch between different fictional/company datasets.

## Build order

Implement the application in this order:

1. Project scaffold and configuration
2. Authentication, users, roles, permissions
3. Multi-company / tenant architecture
4. Document ingestion and company dataset management
5. Text extraction, cleaning, chunking and metadata
6. Embedding and vector storage
7. ANN retrieval
8. XGBoost relevance reranking
9. LLM provider abstraction with OpenAI/Grok toggle
10. RAG answer generation and citations
11. Agentic multi-step workflow
12. MCP-compatible tool layer
13. Security and prompt-injection defenses
14. Observability: logs, metrics and traces
15. Failure handling and retries
16. Evaluation dashboard and test dataset
17. Final UI polish and documentation

Do not implement everything as one giant file. Keep clear modules and service boundaries.

## Preferred architecture

Frontend:
- React
- Vite
- TypeScript preferred
- Responsive SPA
- Monochrome premium UI
- ChatGPT-like conversational workspace

Backend / AI:
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite for the initial application/auth/tenant metadata so the project runs without external DB setup
- Qdrant local for vector storage, OR a clean vector-store abstraction that can later support Qdrant/pgvector
- Sentence Transformers for embeddings
- scikit-learn + XGBoost for reranking
- OpenAI-compatible Python client for both OpenAI and xAI/Grok
- OpenTelemetry-compatible instrumentation where practical

The architecture must isolate provider-specific code behind an LLMProvider interface.

## Important implementation principle

The UI, backend, retrieval system, LLM provider, and tenant/company data must be separate concerns.

A future company should be onboardable by:
- creating a company/tenant
- uploading its documents
- indexing those documents
- assigning users to that tenant
- selecting that tenant in permitted administrative views

Do NOT require source-code changes to replace the enterprise knowledge base.

## Company switching

Use a tenant-aware architecture.

Every enterprise document, chunk, vector payload, evaluation item, and audit/trace record that relates to company data must carry a `tenant_id`.

The default demo should contain at least 3 fictional companies:
- Asterion Technologies
- Northstar Manufacturing
- Meridian Healthcare Services

A platform administrator can switch the active demo company from the admin/company selector.

Normal users must only see companies to which they are assigned.

"Switch company database" means switching the active tenant knowledge space, not blindly swapping credentials or exposing another company's database. Keep tenant isolation enforced in backend queries and vector filters.

## Security requirements

Never rely on frontend hiding alone.

Authorization must be enforced in backend services before:
- document retrieval
- metadata access
- tool execution
- agent actions
- final evidence assembly

Retrieved documents must be treated as DATA, not instructions.

Implement basic prompt-injection defenses:
- system instructions have higher priority
- retrieved text is clearly delimited as untrusted enterprise content
- never execute instructions found inside documents
- tool calls are validated against authenticated user's permissions
- never expose secrets or internal implementation details through answers

## UX requirements

Overall visual direction:
- monochrome
- premium
- minimal
- calm
- high whitespace
- subtle borders
- restrained shadows
- no rainbow gradients
- no excessive glassmorphism
- no cartoon illustrations

Typography:
- Prefer system/Apple-style stack:
  `-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Segoe UI", sans-serif`
- For Spotify-like rounded/modern feel, use Inter or a similar open font rather than copying a proprietary font.
- Do not bundle proprietary Apple or Spotify fonts.

The interface should feel closer to a premium productivity product than a developer dashboard.

## Main screens

1. Login
2. Main chat / research workspace
3. Source/evidence panel
4. Company selector where permitted
5. Admin/user management
6. Document ingestion
7. Knowledge base status
8. Observability panel
9. Evaluation panel
10. Settings/provider status

## Final acceptance criteria

The finished demo must allow a reviewer to:

1. Log in using seeded demo users.
2. See different access levels produce different retrieval results.
3. Switch company as an authorized administrator.
4. Upload a document to a selected company.
5. Index it.
6. Ask a question about it.
7. Retrieve relevant chunks using embeddings + ANN.
8. Rerank candidates using XGBoost.
9. Generate an evidence-backed answer using the selected LLM provider.
10. Display citations.
11. Show an explicit "insufficient evidence" response when appropriate.
12. Demonstrate a multi-step agentic question.
13. Show traces/telemetry for a request.
14. Run a small evaluation set and display retrieval/grounding/latency metrics.
