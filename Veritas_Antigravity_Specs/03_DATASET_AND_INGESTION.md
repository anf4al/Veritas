# PART 3 — INITIAL ENTERPRISE DATASET AND INGESTION

## Dataset goal

Create a connected, realistic synthetic enterprise dataset large enough to demonstrate:
- semantic retrieval
- filtering
- reranking
- version conflicts
- outdated documents
- citations
- multi-step investigation
- permissions
- cross-document reasoning

Do not generate hundreds of unrelated random paragraphs.

The documents should reference the same entities so that questions can require connecting evidence.

## Initial scale

Generate at least:
- 3 fictional companies
- 60 documents per company
- 180 documents total
- 20–40 chunks per document on average where appropriate
- target roughly 5,000–7,000 chunks total

The generator should be deterministic using a seed.

## Company 1 — Asterion Technologies

Departments:
- HR
- Finance
- Procurement
- Operations
- Information Security
- Legal
- Product
- Engineering
- Compliance

Entities:
- vendors
- employees
- products
- contracts
- policies
- incidents
- business processes

## Company 2 — Northstar Manufacturing

Departments:
- HR
- Procurement
- Manufacturing
- Quality
- Logistics
- Safety
- IT
- Finance
- Legal

Entities:
- suppliers
- factories
- machines
- quality incidents
- contracts
- logistics partners
- safety procedures

## Company 3 — Meridian Healthcare Services

Departments:
- Compliance
- Clinical Operations
- HR
- Procurement
- IT
- Legal
- Finance
- Facilities

Entities:
- vendors
- compliance policies
- data-retention rules
- operational procedures
- contracts
- audit findings

## Document types

Generate realistic documents including:

HR:
- employee handbook
- leave policy
- WFH policy
- reimbursement policy
- travel policy
- disciplinary procedure
- onboarding SOP

Procurement:
- procurement policy
- supplier evaluation policy
- vendor onboarding SOP
- purchase approval matrix
- SLA policy
- supplier performance reports

Legal:
- vendor contracts
- master service agreements
- termination clauses
- renewal clauses
- confidentiality clauses

Security:
- information security policy
- access control policy
- incident response policy
- password policy
- data retention policy
- security incident reports

Operations:
- quarterly operational reports
- SOPs
- process manuals
- incident summaries

Product/technical:
- product manuals
- deployment guides
- architecture notes
- support procedures

Compliance:
- audit reports
- compliance policies
- risk assessments
- corrective action plans

## Deliberate retrieval challenges

Include:
- 2024 and 2025 versions of some policies
- 2026 current versions
- outdated policies
- duplicate documents
- similar documents with different meanings
- contradictory clauses
- documents with noisy formatting
- repeated headers/footers
- tables converted into imperfect text
- references from one document to another

Example:
A vendor performance report says Vendor Atlas missed SLA targets three times.
The vendor contract contains a termination clause.
The procurement policy defines what qualifies as a high-risk supplier.
The risk assessment flags Vendor Atlas.
The agent should be able to connect these documents.

## Seed questions

Include evaluation questions such as:
1. What is the current WFH policy?
2. How many annual leave days can an employee carry forward?
3. What changed between the 2025 and 2026 procurement policies?
4. Which suppliers violated their SLA more than twice?
5. Why was Vendor Atlas classified as high risk?
6. Does the current Vendor Atlas contract permit termination for repeated SLA violations?
7. Which information-security procedures changed between 2025 and 2026?
8. Which contracts expire within 90 days?
9. Which policies mention data retention?
10. Compare the current reimbursement policy with the previous version.

## Dataset generation

Implement a script such as:
`backend/scripts/generate_demo_dataset.py`

It should generate:
- source documents
- metadata
- seed users
- companies
- relationships
- evaluation questions

Keep source data under:
`data/seed/`

Do not hard-code the entire dataset directly inside Python business logic.

## Ingestion pipeline

For each document:

1. extract text
2. clean text
3. preserve page numbers where available
4. identify sections where possible
5. chunk by semantic/document structure
6. add modest overlap
7. create embedding
8. store vector + text + metadata
9. preserve company_id and permission metadata

Metadata must include enough information to produce citations.
