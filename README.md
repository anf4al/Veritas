# Veritas — Enterprise Intelligence & Research Platform

**Veritas** is a production-minded enterprise intelligence and research platform designed for natural-language questioning over private enterprise knowledge bases. Veritas combines enterprise Retrieval-Augmented Generation (RAG), multi-tenant Role-Based Access Control (RBAC), multi-step agentic retrieval, XGBoost relevance reranking, and an OpenAI/xAI Grok provider abstraction into a clean, monochrome workspace.

---

## Key Features

1. **Enterprise Multi-Tenancy & Zero-Trust Knowledge Isolation**:
   - Every document, chunk, vector payload, and audit record is partitioned by `tenant_id`.
   - Vector searches strictly filter by tenant and permission level *before* candidate assembly.
   - Pre-seeded with 3 fictional companies: **Asterion Technologies**, **Northstar Manufacturing**, and **Meridian Healthcare Services**.
   - Authorized platform administrators can switch active company workspaces on the fly.

2. **Fine-Grained Role-Based Access Control (RBAC)**:
   - 8 seeded enterprise roles (`PLATFORM_ADMIN`, `COMPANY_ADMIN`, `HR_MANAGER`, `OPERATIONS_MANAGER`, `SECURITY_OFFICER`, `SALES`, `EMPLOYEE`, `COMPLIANCE_OFFICER`).
   - Granular document-level permission checking: standard employees cannot access confidential contracts or security incident reports; HR managers cannot access IT security investigations; salary records are strictly protected.

3. **Hybrid RAG & XGBoost Relevance Reranking**:
   - Query embedding using `sentence-transformers/all-MiniLM-L6-v2`.
   - High-performance Approximate Nearest Neighbor (ANN) vector candidate retrieval.
   - Machine learning reranking with an **XGBoost** relevance classifier evaluating 10 lexical, metadata, recency, and currentness features (e.g. 2026 active policies vs. outdated 2024/2025 versions).

4. **Multi-Step Agentic Retrieval & 6 Core Enterprise Tools**:
   - Orchestration layer with planning, tool budgets (max 10 tool calls, max 8 steps), and loop prevention.
   - 6 Core tools: `search_enterprise_knowledge`, `get_document`, `compare_documents`, `find_contracts_expiring`, `get_vendor_performance`, and `get_policy_versions`.
   - Standard **Model Context Protocol (MCP)** JSON-RPC server adapter (`/api/v1/tools/mcp/rpc`).

5. **LLM Provider Abstraction (`OpenAI` / `Grok`)**:
   - Toggle seamlessly between OpenAI and xAI Grok using exactly 3 environment variables.
   - Grok uses official xAI API compatibility (`https://api.x.ai/v1`).
   - Grounded RAG prompts treating retrieved documents as untrusted data with strict prompt-injection defenses.
   - Citations derived exclusively from verified backend chunk metadata.

6. **Observability, Tracing & Evaluation Benchmarking**:
   - OpenTelemetry-compatible traces with span breakdowns (`auth`, `agent_planning`, `vector_search`, `reranking`, `tool_call`, `llm_generate`).
   - Real-time latency metrics: p95 latency, average component breakdown, tool call counts.
   - Benchmark evaluation runner computing empirical **Recall@5/10/20**, **XGBoost Ranking Lift**, and groundedness scores.

7. **Monochrome Premium User Interface**:
   - Built with React, Vite, TypeScript, and Tailwind CSS.
   - System font typography (`SF Pro / Inter / Segoe UI`), subtle borders, high whitespace.
   - Interactive conversational feed, clickable citation pills, slide-out evidence drawer, and administrative consoles.

---

## Seeded Demo Credentials

Veritas includes 8 pre-seeded accounts for immediate testing:

| Role | Username | Password | Permitted Companies | Access Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Platform Administrator** | `admin@veritas.demo` | `VeritasAdmin!2026` | All Companies | Full system management, tenant switching, observability, and evaluation. |
| **HR Manager** | `hr@asterion.demo` | `VeritasHR!2026` | Asterion Technologies | HR handbooks, leave, reimbursement, HR SOPs. No salary or security incidents. |
| **Operations Manager** | `ops@asterion.demo` | `VeritasOps!2026` | Asterion Technologies | Procurement, vendors, SLAs, ops reports. No HR-confidential files. |
| **Security Officer** | `security@asterion.demo` | `VeritasSec!2026` | Asterion Technologies | InfoSec policies, incidents, data retention, audits. No salary records. |
| **Sales Lead** | `sales@asterion.demo` | `VeritasSales!2026` | Asterion Technologies | Product documentation, approved pricing, customer materials. |
| **Standard Employee** | `employee@asterion.demo` | `VeritasEmployee!2026` | Asterion Technologies | General handbooks, leave, WFH, reimbursement. No confidential files. |
| **Northstar Admin** | `admin@northstar.demo` | `NorthstarAdmin!2026` | Northstar Manufacturing | Document & user management strictly for Northstar. |
| **Meridian Compliance** | `compliance@meridian.demo` | `MeridianCompliance!2026` | Meridian Healthcare | Compliance, clinical guidelines, and audits strictly for Meridian. |

---

## Environment Configuration

Per specification, the `.env` file contains exactly three application settings:

```env
AI_PROVIDER=openai
GROK_API_KEY=
OPENAI_API_KEY=
```

- `AI_PROVIDER`: Set to `openai` or `grok`.
- `OPENAI_API_KEY`: Required when `AI_PROVIDER=openai`.
- `GROK_API_KEY`: Required when `AI_PROVIDER=grok`.
- *Note:* If API keys are blank, Veritas runs in high-fidelity local emulation mode so all features, retrieval paths, and benchmarks remain testable offline.

---

## Quickstart Guide

### 1. Setup Backend Environment

```powershell
# Create and activate virtual environment
python -m venv backend/.venv
backend\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Generate Dataset & Seed Database

```powershell
$env:PYTHONPATH="."
python -m backend.scripts.seed_database
```
*This generates 182 interconnected documents across the 3 companies into `data/seed/`, creates the SQLite schema, registers the 8 demo users, and indexes all chunks.*

### 3. Train the XGBoost Reranker

```powershell
$env:PYTHONPATH="."
python -m backend.scripts.train_reranker
```
*Extracts features from synthetic query-document pairs and trains the binary relevance classifier to `backend/app/reranking/reranker.xgb`.*

### 4. Run Backend Tests

```powershell
$env:PYTHONPATH="."
python -m pytest backend/tests -v
```

### 5. Setup & Launch Frontend

```powershell
cd frontend
npm install
npm run dev
```

### 6. Start Backend API Server

```powershell
# In root directory:
$env:PYTHONPATH="."
backend\.venv\Scripts\uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Access the application in your browser at: **`http://localhost:5173`** (or backend docs at `http://127.0.0.1:8000/docs`).

---

## Architecture Overview

```
Veritas/
├── .env.example              # 3-variable environment template
├── backend/
│   ├── app/
│   │   ├── api/v1/           # REST endpoints (auth, companies, documents, chat, tools, observability, eval)
│   │   ├── auth/             # JWT token handling & granular RBAC matrix
│   │   ├── core/             # Configuration, SQLite session, direct bcrypt security
│   │   ├── models/           # SQLAlchemy ORM models (Company, User, Document, Chunk, AuditEvent, EvaluationRun)
│   │   ├── ingestion/        # Document extraction (PDF, DOCX, TXT), cleaning, structural chunker
│   │   ├── retrieval/        # Sentence-transformers embedding & tenant-partitioned ANN vector store
│   │   ├── reranking/        # 10-feature extractor & XGBoost classifier
│   │   ├── llm/              # Unified LLMProvider: OpenAIProvider vs GrokProvider
│   │   ├── tools/            # 6 Core enterprise tools
│   │   ├── agents/           # Multi-step orchestrator, prompt-injection delimiters, loop safeguards
│   │   ├── mcp/              # Model Context Protocol JSON-RPC server adapter
│   │   ├── observability/    # Telemetry, OpenTelemetry-compatible traces & spans, metrics
│   │   └── evaluation/       # Seed benchmark dataset, Recall@K, XGBoost lift calculator
│   ├── scripts/              # Dataset generator, database seeder, XGBoost trainer
│   └── tests/                # 16 unit & integration tests
├── data/
│   ├── seed/                 # 182 generated synthetic documents & metadata.json
│   └── uploads/              # Ingested user uploads
├── frontend/
│   ├── src/
│   │   ├── components/       # ChatWorkspace, EvidenceDrawer, Sidebar, Admin tabs, DemoAccountsModal
│   │   ├── context/          # AuthContext managing session & tenant switching
│   │   ├── services/         # API client
│   │   └── pages/            # LoginPage & DashboardPage
│   ├── package.json
│   └── vite.config.ts
```

---

## Verification & Acceptance Checklist

- [x] Seeded demo users can log in via username/password with bcrypt hashing.
- [x] Access levels produce different retrieval results (standard employees cannot view confidential security incidents or contracts).
- [x] Platform admin can switch active companies (Asterion, Northstar, Meridian) with immediate workspace and tenant data isolation.
- [x] Documents can be uploaded, cleaned, chunked, and indexed via the Document Ingestion view.
- [x] Semantic vector retrieval uses dense embeddings with strict tenant partitioning.
- [x] XGBoost relevance reranker sorts candidate chunks based on learned features.
- [x] Evidence-backed answers are generated with verified chunk metadata citations.
- [x] Multi-step agent questions (e.g. Vendor Atlas SLA breach vs. contract termination clause) coordinate multiple tools.
- [x] OpenTelemetry-compatible traces and latency metrics are tracked in the Observability tab.
- [x] Evaluation benchmarks calculate empirical Recall@5/10/20, groundedness, and XGBoost ranking improvements.
