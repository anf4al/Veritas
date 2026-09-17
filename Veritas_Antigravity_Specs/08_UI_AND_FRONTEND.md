# PART 8 — FRONTEND / UI SPECIFICATION

## Visual language

Use a basic monochrome palette:
- near-black
- white
- soft gray
- border gray
- muted secondary text

Avoid:
- bright gradients
- neon
- excessive colors
- heavy shadows
- glassmorphism everywhere

Use color only when necessary for:
- success
- warning
- error
- permission state

Keep these restrained.

## Typography

Use a premium system stack:

```css
font-family:
  -apple-system,
  BlinkMacSystemFont,
  "SF Pro Display",
  "SF Pro Text",
  "Inter",
  "Segoe UI",
  sans-serif;
```

Use Inter or another open-source equivalent if a bundled font is required. Do not bundle proprietary Apple/Spotify fonts.

## Login page

Design:
- centered Veritas wordmark
- username
- password
- sign-in button
- subtle "Demo accounts" link/panel
- clean white/black composition

Demo account panel can list usernames but should require the user to click to reveal passwords.

## Main workspace

ChatGPT-like structure:

Left sidebar:
- Veritas logo
- New research
- recent conversations
- active company
- user profile
- admin navigation when authorized

Main:
- welcome/empty state
- chat messages
- streaming response
- source citations
- evidence expand/collapse
- loading state
- retry

Right evidence panel:
- source documents
- page/section
- version
- effective date
- relevance/rerank indicator
- open source details

## Company switcher

Only visible for authorized users.

Show:
- company name
- status
- document count
- indexed chunk count

Changing company must refresh:
- chat context
- available data
- source list
- permissions

## Admin pages

Users:
- list users
- role
- company
- permissions
- status

Documents:
- upload
- index status
- version
- department
- confidentiality
- company

Knowledge:
- chunk count
- vector count
- last indexing time

Observability:
- recent traces
- latency
- tool calls
- errors

Evaluation:
- Recall@K
- groundedness
- correctness
- latency
- run comparison

## Chat behavior

Support natural questions.

Examples:
- "What is our WFH policy?"
- "What changed in procurement policy?"
- "Which suppliers violated SLAs?"
- "Compare the 2025 and 2026 security policies."
- "Why was Vendor Atlas flagged high risk?"
- "Does our current contract allow termination?"

If question is outside enterprise knowledge:
"I can only answer using the authorized enterprise knowledge available in Veritas."

## Responsive behavior

Desktop-first but responsive.

Do not create an overcomplicated mobile app.

## Accessibility

Use:
- keyboard navigation
- visible focus states
- semantic buttons
- adequate contrast
- readable font sizes
