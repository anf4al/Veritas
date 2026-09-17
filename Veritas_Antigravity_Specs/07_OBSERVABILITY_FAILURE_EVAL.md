# PART 7 — OBSERVABILITY, FAILURE HANDLING AND EVALUATION

## Observability

Implement structured telemetry around:
- authentication
- retrieval
- reranking
- tool calls
- agent steps
- LLM calls
- verification
- total request

### Logs

Examples:
- login success/failure
- retrieval started/completed
- tool invoked
- LLM request failed
- insufficient evidence
- authorization denied

Never log passwords, API keys, tokens or sensitive document contents unnecessarily.

### Metrics

Track:
- request count
- error count
- average/p95 latency
- retrieval latency
- reranking latency
- LLM latency
- token usage when available
- number of tool calls
- cache hit rate
- retrieval Recall@K during evaluation
- groundedness/evaluation scores

### Traces

A trace represents one end-to-end request.

Example:

Trace: `abc123`

- authentication span
- agent span
- embedding span
- vector-search span
- reranking span
- tool-call span
- LLM span
- verification span
- final response span

Each span should include safe timing and diagnostic attributes.

If practical, use OpenTelemetry-compatible tracing.

## Failure handling

Possible failures:
- invalid login
- unauthorized access
- vector DB unavailable
- embedding failure
- LLM timeout
- LLM provider error
- tool failure
- database failure
- no evidence
- conflicting evidence
- agent loop limit
- evaluation failure

Rules:
1. Retry only transient failures.
2. Use bounded retries.
3. Never retry forever.
4. Never answer from unsupported model knowledge when enterprise evidence is required.
5. Distinguish:
   - retrieval failed
   - retrieval succeeded but no evidence was sufficient
6. Give the user a useful, non-technical message.
7. Keep technical diagnostic details in logs/traces.

## Example graceful errors

Retrieval system unavailable:
"The enterprise knowledge base is temporarily unavailable. Please try again."

No sufficient evidence:
"I couldn't find sufficient authorized information in the enterprise knowledge base to answer that reliably."

Provider failure:
"The selected AI provider is temporarily unavailable. Please try again."

Authorization:
"You do not have access to the information required for this request."

## Caching

Add a small caching abstraction.

Potential cache layers:
- query embedding cache
- retrieval cache
- answer cache where safe

Cached answers must be associated with relevant document/version state.

Invalidate or bypass cached answers when underlying documents change.

Do not sacrifice authorization for caching.

## Evaluation

Create an evaluation dataset containing:
- question
- expected evidence chunk/document IDs
- expected answer or answer criteria
- tenant
- minimum required permissions

Metrics:

Retrieval:
- Recall@5
- Recall@10
- Recall@20
- Precision@K where applicable

Reranking:
- compare ANN ranking with XGBoost ranking
- measure whether relevant chunks move upward

Generation:
- answer correctness
- groundedness/faithfulness
- citation correctness

System:
- latency
- token usage
- cost estimate
- error rate
- tool-call count

## Evaluation workflow

1. Run evaluation set.
2. Collect retrieval results.
3. Calculate retrieval metrics.
4. Generate answers.
5. Evaluate groundedness/correctness.
6. collect latency/cost.
7. show results in admin evaluation page.
8. allow comparing two runs.

Do not manufacture impressive metrics. Display actual measured results.

## Regression testing

Whenever changing:
- embedding model
- chunking strategy
- retrieval K
- XGBoost model
- prompt
- LLM provider/model

run the evaluation set and compare results.

The goal is not merely "better-looking answers"; it is measurable system improvement.
