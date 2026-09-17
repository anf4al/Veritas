# PART 2 — MULTI-COMPANY / TENANT KNOWLEDGE BASE

## Goal

Veritas must be reusable for different companies without rewriting the application.

Do NOT hard-code Asterion's documents into retrieval logic.

Every company is a tenant.

## Core entities

Implement at least:

Company:
- id
- name
- slug
- description
- status
- created_at

User:
- id
- username
- password_hash
- display_name
- role
- status

UserCompany:
- user_id
- company_id

Document:
- id
- company_id
- title
- filename
- document_type
- department
- version
- effective_date
- status
- confidentiality
- source
- checksum
- created_at

Chunk:
- id
- document_id
- company_id
- chunk_index
- text
- page
- section
- metadata_json

AuditEvent:
- id
- company_id
- user_id
- action
- timestamp
- details

## Company switching

Platform admin:
- can select Asterion, Northstar or Meridian
- all subsequent admin operations use selected tenant

Company admin:
- can operate only within their assigned company

Normal employee:
- cannot arbitrarily switch company

Every backend service receiving a company_id must verify the authenticated user is authorized for that company.

## Uploading another company's data

Create an admin workflow:

1. Select company.
2. Upload one or more PDF/TXT/DOCX files.
3. Extract text.
4. Clean text.
5. Chunk text.
6. Attach document metadata.
7. Generate embeddings.
8. Store chunks/vectors under that company.
9. Mark document as indexed.
10. Show ingestion status.

The system should make it possible to onboard a new company later without changing source code.

## Isolation

Vector searches MUST filter by tenant/company ID.

Never run:
`search(all_vectors)`

Instead conceptually:
`search(vectors, tenant_id=current_user.company_id, permission_filters=...)`

This prevents cross-company leakage.

## Future extensibility

Keep a `TenantKnowledgeStore` abstraction so the project can later support:
- one shared database with tenant_id
- separate schemas
- separate vector collections
- separate databases
- customer-managed storage

The initial demo can use one local database/vector service with strict tenant filters.
