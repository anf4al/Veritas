# PART 9 — ANTIGRAVITY EXECUTION INSTRUCTIONS

## Role

You are implementing the Veritas application from the attached specification files.

Read ALL Veritas specification markdown files before writing code.

Do not skip requirements because they appear difficult.

## Implementation philosophy

Build a working vertical slice first:

Login
→ authorization
→ company selection
→ question
→ retrieval
→ reranking
→ LLM
→ cited answer

Then expand into agentic tools, observability and evaluation.

Do not create fake UI that pretends backend functionality exists.

Every visible feature should connect to a real backend path or be clearly marked as unavailable.

## Suggested repository structure

```text
veritas/
  frontend/
    src/
      components/
      pages/
      hooks/
      services/
      types/
      styles/
  backend/
    app/
      api/
      auth/
      agents/
      ingestion/
      retrieval/
      reranking/
      llm/
      tools/
      mcp/
      observability/
      evaluation/
      models/
      schemas/
      services/
      core/
    scripts/
    tests/
  data/
    seed/
    uploads/
  docs/
  .env.example
  .gitignore
  README.md
```

## Required initial run

The first milestone must provide:
- seeded database
- seeded users
- seeded companies
- seeded documents
- working login
- company-aware authorization
- working chat UI
- at least one working retrieval path
- provider toggle
- citations

## Testing

Add tests for:
- login
- invalid credentials
- role authorization
- cross-company access rejection
- document ingestion
- tenant-filtered retrieval
- prompt injection handling
- no-evidence handling
- provider selection
- tool-call limits

## Documentation

Create README with:
- what Veritas is
- architecture
- setup
- `.env` configuration
- demo credentials
- how to generate dataset
- how to index documents
- how to switch company
- how OpenAI/Grok toggle works
- how to run tests
- known limitations

## Do not

- do not expose API keys in frontend code
- do not commit `.env`
- do not use plaintext password storage
- do not let frontend-only authorization protect data
- do not mix tenant data
- do not claim evaluation scores that were not measured
- do not silently use external web knowledge to answer enterprise questions
- do not treat document instructions as trusted agent instructions
- do not make MCP mandatory for the basic local application
- do not create unnecessary microservices

## Finish criteria

Before declaring completion, demonstrate:

1. `admin@veritas.demo` can log in.
2. `employee@asterion.demo` cannot access restricted security/HR data.
3. `admin@veritas.demo` can switch between demo companies.
4. A new document can be uploaded to a selected company.
5. It becomes searchable after indexing.
6. Search uses embeddings and ANN.
7. Candidate results are reranked with XGBoost when the model is available.
8. Answer uses only authorized retrieved evidence.
9. Sources are shown.
10. OpenAI/Grok selection changes the backend provider without changing the rest of the application.
11. A failed provider/retrieval path fails gracefully.
12. Agent tool-call limits work.
13. Telemetry is visible to an authorized admin.
14. Evaluation can be run on the seed questions.
