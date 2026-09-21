\# Veritas Development Roadmap



Veritas is being developed incrementally to explore modern AI engineering concepts while preserving its existing RAG, security, and evaluation architecture.



\## Current Foundation



\- Python + FastAPI

\- React + TypeScript

\- RAG pipeline

\- Sentence Transformers embeddings

\- Custom vector retrieval

\- XGBoost reranking

\- Deterministic evidence gate

\- JWT authentication and RBAC

\- Multi-tenant isolation

\- MCP tooling

\- Groq LLM integration

\- Automated RAG evaluation benchmarks



\## Planned Evolution



\### 1. LangChain

Learn and integrate LangChain concepts gradually:

\- Model abstractions

\- Prompt templates

\- Documents

\- Retrievers

\- Tools

\- Structured output

\- RAG components



\### 2. LangGraph

Evolve the current orchestrator into a stateful agent workflow:

\- State

\- Nodes

\- Edges

\- Conditional routing

\- Loops and retries

\- Tool calling

\- Multi-step research



\### 3. Vector Database

Evaluate vector-storage options:

\- Chroma

\- Pinecone

\- Weaviate

\- FAISS



Use Veritas evaluation benchmarks to compare retrieval quality before replacing the existing implementation.



\### 4. LangFuse

Add deeper observability:

\- LLM traces

\- Token usage

\- Cost tracking

\- Latency

\- Retrieval/agent traces

\- Evaluation visibility



\### 5. Docker

Containerize the application and its supporting services.



\### 6. Cloud Deployment

Deploy Veritas to AWS or GCP and learn:

\- Cloud infrastructure

\- Secrets

\- Networking

\- Database hosting

\- Storage

\- Monitoring



\### 7. LoRA / QLoRA

Explore fine-tuning only after understanding the existing RAG and evaluation pipeline.



Potential applications include domain-specific classification, structured outputs, or specialized enterprise tasks.



\## Evaluation-Driven Development



Existing evaluation benchmarks will be used as an offline feedback loop when modifying the retrieval or ranking pipeline.



Changes to chunking, retrieval parameters, reranking, or retrieval logic should be benchmarked against a baseline to identify improvements and regressions.



Evaluation metrics should guide development and optimization, not directly control live retrieval decisions.



\## Core Principle



New frameworks and technologies should be introduced only when they solve a real engineering problem or provide a meaningful learning opportunity.



Existing security and reliability controls, especially tenant isolation and the deterministic evidence gate, should remain under explicit application control.

