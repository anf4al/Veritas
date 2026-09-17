# PART 1 — AUTHENTICATION, USERS, ROLES AND ACCESS CONTROL

## Login

Create a clean login page with:
- username
- password
- show/hide password
- sign in button
- subtle loading state
- clear invalid-credential message
- Veritas branding

Do not expose passwords anywhere except the seeded demo credentials section of the developer documentation.

Use secure password hashing in the backend. Do not store plaintext passwords in the database.

Use session/JWT authentication with a short-lived access token and secure handling.

## Seeded demo accounts

Create these demo users for the initial installation:

### Platform administrator
Username: `admin@veritas.demo`
Password: `VeritasAdmin!2026`
Role: PLATFORM_ADMIN
Companies: all
Access: can manage users, companies, documents, indexing, evaluation, observability and company switching.

### HR manager
Username: `hr@asterion.demo`
Password: `VeritasHR!2026`
Role: HR_MANAGER
Company: Asterion Technologies
Access:
- HR policies
- employee handbook
- leave/reimbursement information
- HR-related SOPs
Cannot access salary-confidential records or security incident investigations.

### Operations manager
Username: `ops@asterion.demo`
Password: `VeritasOps!2026`
Role: OPERATIONS_MANAGER
Company: Asterion Technologies
Access:
- procurement
- vendors
- SLAs
- operational reports
- product/process documentation
Cannot access HR-confidential records.

### Security/compliance officer
Username: `security@asterion.demo`
Password: `VeritasSec!2026`
Role: SECURITY_OFFICER
Company: Asterion Technologies
Access:
- information security policies
- incidents
- compliance
- data retention
- audit documentation
Cannot access employee salary records.

### Sales user
Username: `sales@asterion.demo`
Password: `VeritasSales!2026`
Role: SALES
Company: Asterion Technologies
Access:
- product documentation
- approved pricing/product information
- customer-facing material
Cannot access HR, salary, confidential security incidents or legal-confidential contracts.

### Standard employee
Username: `employee@asterion.demo`
Password: `VeritasEmployee!2026`
Role: EMPLOYEE
Company: Asterion Technologies
Access:
- general employee handbook
- leave policy
- WFH policy
- reimbursement policy
Cannot access restricted HR records, security incidents, contracts or management-only reports.

### Northstar administrator
Username: `admin@northstar.demo`
Password: `NorthstarAdmin!2026`
Role: COMPANY_ADMIN
Company: Northstar Manufacturing
Access: manage users/documents for Northstar only.

### Meridian compliance user
Username: `compliance@meridian.demo`
Password: `MeridianCompliance!2026`
Role: COMPLIANCE_OFFICER
Company: Meridian Healthcare Services
Access: compliance, policy and audit material for Meridian only.

These credentials are DEMO credentials only. Clearly label them as development/demo accounts in the UI or documentation.

## Authorization model

Use role + permission + tenant scope.

Example permissions:
- `company.read`
- `company.switch`
- `user.read`
- `user.manage`
- `document.read`
- `document.upload`
- `document.delete`
- `knowledge.index`
- `knowledge.search`
- `knowledge.search.restricted`
- `observability.read`
- `evaluation.read`
- `evaluation.run`
- `admin.all`

Do not assume a role alone is sufficient. The backend should check the actual permission and tenant scope.

## Backend enforcement

Every protected endpoint must identify:
- authenticated user
- active tenant
- user's tenant memberships
- user's permissions

Reject unauthorized requests before database/vector retrieval.

The frontend may hide unavailable UI elements for usability, but backend authorization is the real security boundary.

## Login success

After login:
- load user profile
- determine accessible companies
- choose active company
- redirect to research workspace

Platform admin sees company switcher.
Regular users see only their permitted company.
