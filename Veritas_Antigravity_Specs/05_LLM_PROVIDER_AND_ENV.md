# PART 5 — OPENAI/GROK PROVIDER TOGGLE AND .ENV

## Required .env variables

The user specifically wants exactly three application secrets/settings in `.env`:

```env
AI_PROVIDER=openai
GROK_API_KEY=
OPENAI_API_KEY=
```

`AI_PROVIDER` accepts:
- `openai`
- `grok`

Do not commit `.env` to git.

Create `.env.example` with blank keys.

## Provider behavior

When:
`AI_PROVIDER=openai`

Use the OpenAI client and OpenAI model configured in the provider module.

When:
`AI_PROVIDER=grok`

Use the same OpenAI-compatible client abstraction but point it at the xAI API base URL:
`https://api.x.ai/v1`

Use the current supported Grok model configured in one provider constant. Do not scatter model names throughout the application.

The xAI API currently exposes an OpenAI-compatible API and documents using the OpenAI Python client with `base_url="https://api.x.ai/v1"`. Use the Responses API for new integrations where supported. Source: official xAI documentation.

## Provider interface

Create something like:

```text
LLMProvider
  generate()
  generate_structured()
  stream()
```

Implement:
- OpenAIProvider
- GrokProvider

Then:

```text
AI_PROVIDER=openai
        ↓
OpenAIProvider

AI_PROVIDER=grok
        ↓
GrokProvider
```

The rest of Veritas should not care which provider is active.

## Startup validation

On backend startup:
- read AI_PROVIDER
- validate that the corresponding key exists
- fail clearly if provider is selected but key is missing

Do not print API keys to logs.

Expose a safe provider-status endpoint that only says:
- provider selected
- key configured: yes/no
Never expose the secret.

## Important security

Never send either API key to the React frontend.

Only the backend should access `.env`.

## Model selection

Keep model names in one configuration/provider module.

For example:
- OpenAI model: choose a current text-capable model appropriate for the project
- Grok model: use a current supported Grok model

Do not hard-code model names across service files.

## Provider fallback

Do NOT silently fall back from one provider to another if the selected provider fails. That makes debugging and cost control unclear.

If the selected provider fails:
- retry within safe limits
- return graceful error
- log the failure
- preserve provider selection

## Documentation note

The xAI API is OpenAI-compatible, which makes this abstraction practical. Official xAI documentation currently recommends the Responses API for new integrations and shows use of the OpenAI Python client with `https://api.x.ai/v1`.
