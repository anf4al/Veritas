import os
import json
import random
from pathlib import Path
from typing import List, Dict, Any

SEED = 42
random.seed(SEED)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SEED_DIR = ROOT_DIR / "data" / "seed"

COMPANIES = [
    {
        "name": "Asterion Technologies",
        "slug": "asterion",
        "description": "Enterprise cloud infrastructure, cybersecurity, and SaaS software engineering services.",
        "departments": ["HR", "Finance", "Procurement", "Operations", "Information Security", "Legal", "Product", "Engineering", "Compliance"]
    },
    {
        "name": "Northstar Manufacturing",
        "slug": "northstar",
        "description": "Precision automotive components, heavy robotics, and smart industrial automation manufacturing.",
        "departments": ["HR", "Procurement", "Manufacturing", "Quality", "Logistics", "Safety", "IT", "Finance", "Legal"]
    },
    {
        "name": "Meridian Healthcare Services",
        "slug": "meridian",
        "description": "Multi-regional hospital networks, clinical diagnostic operations, and HIPAA-compliant patient management.",
        "departments": ["Compliance", "Clinical Operations", "HR", "Procurement", "IT", "Legal", "Finance", "Facilities"]
    }
]

def generate_asterion_core_docs() -> List[Dict[str, Any]]:
    docs = []

    # 1. WFH Policies (2024, 2025, 2026)
    docs.append({
        "title": "Work From Home Policy 2026",
        "filename": "wfh_policy_2026.md",
        "document_type": "policy",
        "department": "HR",
        "version": "3.0",
        "effective_date": "2026-01-01",
        "confidentiality": "internal",
        "content": """# Work From Home Policy 2026 (Current Active Version)
Document ID: AST-HR-POL-2026-004
Effective Date: January 1, 2026
Supersedes: AST-HR-POL-2025-002

## 1. Scope and Eligibility
All full-time employees at Asterion Technologies are eligible for the hybrid flexible work arrangement following completion of their standard 90-day probationary period.

## 2. Core Working Schedule
Under the 2026 Policy, employees are required to work on-site at their designated regional office a minimum of two (2) core days per calendar week (Tuesday and Thursday). The remaining three (3) business days may be worked remotely from an authorized domestic location.

## 3. Home Workspace Stipend
Eligible remote staff are entitled to a one-time equipment reimbursement stipend of $1,200 upon hire, plus a recurring monthly connectivity allowance of $75 for high-speed broadband.

## 4. Security Requirements
All remote devices connecting to the Asterion corporate network must maintain an active corporate VPN connection, run the required CrowdStrike endpoint security agent, and utilize hardware multi-factor authentication (FIDO2/YubiKey)."""
    })

    docs.append({
        "title": "Work From Home Policy 2025",
        "filename": "wfh_policy_2025.md",
        "document_type": "policy",
        "department": "HR",
        "version": "2.0",
        "effective_date": "2025-01-01",
        "confidentiality": "internal",
        "content": """# Work From Home Policy 2025 (OUTDATED / SUPERSEDED)
Document ID: AST-HR-POL-2025-002
Effective Date: January 1, 2025
Status: Superseded by 2026 Policy

## 1. Core Working Schedule
Under the 2025 Policy, employees were required to work on-site three (3) core days per week (Monday, Wednesday, Friday). Remote work was restricted to two days per week.

## 2. Equipment Allowance
The one-time stipend in 2025 was $800, with a $50 monthly internet reimbursement."""
    })

    # 2. Leave Policy 2026
    docs.append({
        "title": "Leave Policy 2026",
        "filename": "leave_policy_2026.md",
        "document_type": "policy",
        "department": "HR",
        "version": "3.1",
        "effective_date": "2026-01-01",
        "confidentiality": "internal",
        "content": """# Employee Annual and Sick Leave Policy 2026
Document ID: AST-HR-POL-2026-008
Effective Date: January 1, 2026

## 1. Annual Leave Accrual
Full-time permanent employees accrue 22 days of paid annual leave per calendar year, accruing at a rate of 1.83 days per completed month of active service.

## 2. Carry-Forward Rules
Employees may carry forward a maximum of eight (8) unused annual leave days into the subsequent calendar year. Any carried-forward days exceeding eight (8) are automatically forfeited on March 31 unless granted a formal written exception by the Chief People Officer.

## 3. Sick Leave and Medical Absence
Employees receive twelve (12) paid sick leave days per year. Absences extending beyond three (3) consecutive working days require a signed physician certificate."""
    })

    # 3. Reimbursement Policies (2025 vs 2026)
    docs.append({
        "title": "Reimbursement Policy 2026",
        "filename": "reimbursement_policy_2026.md",
        "document_type": "policy",
        "department": "HR",
        "version": "4.0",
        "effective_date": "2026-01-15",
        "confidentiality": "internal",
        "content": """# Business Expense and Reimbursement Policy 2026
Document ID: AST-FIN-POL-2026-011
Effective Date: January 15, 2026

## 1. Daily Meal Allowance
The daily meal per diem for domestic business travel is $95 per day ($20 breakfast, $30 lunch, $45 dinner). Alcohol is non-reimbursable without VP pre-approval.

## 2. Flight and Travel Bookings
Economy class travel is mandatory for domestic flights under six (6) hours. Premium Economy is permitted for flights exceeding six hours. Business Class is authorized only for intercontinental flights over ten (10) hours.

## 3. Receipt Submission Window
All expense reports and itemized receipts must be submitted in Concur within thirty (30) days of expense incurrence."""
    })

    docs.append({
        "title": "Reimbursement Policy 2025",
        "filename": "reimbursement_policy_2025.md",
        "document_type": "policy",
        "department": "HR",
        "version": "3.0",
        "effective_date": "2025-01-01",
        "confidentiality": "internal",
        "content": """# Business Expense and Reimbursement Policy 2025 (SUPERSEDED)
Document ID: AST-FIN-POL-2025-009

## 1. Daily Meal Allowance
The 2025 daily meal per diem was $75 per day ($15 breakfast, $25 lunch, $35 dinner).

## 2. Submission Window
Receipts had to be submitted within 45 days."""
    })

    # 4. Procurement Policies (2025 vs 2026)
    docs.append({
        "title": "Procurement Policy 2026",
        "filename": "procurement_policy_2026.md",
        "document_type": "policy",
        "department": "Procurement",
        "version": "2.2",
        "effective_date": "2026-02-01",
        "confidentiality": "internal",
        "content": """# Enterprise Procurement Policy 2026
Document ID: AST-PROC-POL-2026-003
Effective Date: February 1, 2026

## 1. Purchase Approval Thresholds
- Purchases up to $10,000: Department Manager approval.
- Purchases $10,001 to $50,000: Director approval plus one competitive quote.
- Purchases $50,001 to $250,000: VP approval and minimum three (3) competitive vendor bids.
- Purchases exceeding $250,000: CFO and Procurement Committee approval.

## 2. High-Risk Supplier Classification
A vendor is classified as 'High Risk' if:
- They fail SLA performance benchmarks in three (3) or more consecutive or cumulative reporting periods.
- They incur unresolved Tier-1 security compliance findings.
- Their credit or solvency rating drops below BBB-.

## 3. Contractual Termination Rights
Whenever a supplier is designated High Risk due to repeated SLA defaults, the Procurement Director is empowered to initiate immediate termination for cause under standard contract terms."""
    })

    docs.append({
        "title": "Procurement Policy 2025",
        "filename": "procurement_policy_2025.md",
        "document_type": "policy",
        "department": "Procurement",
        "version": "1.8",
        "effective_date": "2025-01-01",
        "confidentiality": "internal",
        "content": """# Enterprise Procurement Policy 2025 (OUTDATED)
Document ID: AST-PROC-POL-2025-001

## 1. Approval Thresholds
In 2025, purchases up to $5,000 required manager approval; $5,001 to $25,000 required director approval; over $100,000 required CFO approval.

## 2. High Risk Definition
In 2025, high risk required four (4) SLA violations rather than three."""
    })

    # 5. Connected Storyline: Vendor Atlas (Violations, Contract, Risk Assessment)
    docs.append({
        "title": "Vendor Performance Report Q4 2025",
        "filename": "vendor_perf_q4_2025.md",
        "document_type": "report",
        "department": "Operations",
        "version": "1.0",
        "effective_date": "2026-01-10",
        "confidentiality": "internal",
        "content": """# Vendor Performance Report Q4 2025
Document ID: AST-OPS-REP-2025-Q4

## 1. Executive Summary of SLA Compliance
During Q4 2025, vendor performance across tier-1 service providers was monitored against established SLAs.

## 2. Vendor Atlas Incident Summary
Vendor Atlas (managed cloud hosting & storage provider) missed agreed uptime and ticket resolution SLA targets three (3) separate times during the reporting period:
- October 14, 2025: Uptime fell to 98.1% (agreed SLA: 99.95%). Root cause: unannounced network maintenance.
- November 22, 2025: Critical ticket response time was 8.4 hours (agreed SLA: < 1.0 hour).
- December 19, 2025: Unscheduled database outage lasting 3.2 hours.

## 3. Other Suppliers
- Apex Logistics: 1 SLA minor delay recorded in November.
- CloudPulse Networks: Zero SLA violations recorded (99.99% uptime maintained)."""
    })

    docs.append({
        "title": "Vendor Atlas Risk Assessment 2026",
        "filename": "vendor_atlas_risk_assessment_2026.md",
        "document_type": "report",
        "department": "Procurement",
        "version": "1.0",
        "effective_date": "2026-01-20",
        "confidentiality": "internal",
        "content": """# Supplier Risk Assessment: Vendor Atlas
Document ID: AST-PROC-RSK-2026-002
Vendor: Vendor Atlas Systems LLC
Contract Reference: AST-MSA-2023-089

## 1. Risk Rating Classification
Overall Risk Rating: HIGH RISK (CRITICAL)

## 2. Grounds for High-Risk Classification
Vendor Atlas has been classified as High Risk pursuant to Section 2 of the 2026 Procurement Policy due to:
1. Three documented SLA target failures within Q4 2025 (October 14, November 22, and December 19).
2. Recurring failure to deliver Root Cause Analysis (RCA) within mandatory 5-day windows.
3. Increasing customer ticket backlog directly affecting Asterion SaaS customer operations.

## 3. Recommended Action
Recommend exercising contractual remedies under Master Services Agreement AST-MSA-2023-089."""
    })

    docs.append({
        "title": "Vendor Atlas Master Services Agreement",
        "filename": "vendor_atlas_msa.md",
        "document_type": "contract",
        "department": "Legal",
        "version": "2.0",
        "effective_date": "2023-04-01",
        "confidentiality": "confidential",
        "content": """# Master Services Agreement: Asterion Technologies & Vendor Atlas
Contract ID: AST-MSA-2023-089
Effective Date: April 1, 2023
Term: 36 Months (Expires April 1, 2026)

## Section 14: Termination Provisions
### Section 14.1: Termination for Convenience
Either party may terminate this Agreement without cause by providing at least ninety (90) days prior written notice.

### Section 14.2: Termination for Cause and SLA Default
Asterion Technologies may terminate this Agreement immediately for cause upon written notice if the Supplier:
(a) Commits a material breach that remains uncured for fifteen (15) business days; or
(b) Violates agreed Service Level Agreement (SLA) operational targets three (3) or more times within any rolling six-month period. Upon termination under this Section 14.2, no early termination penalties or ongoing hosting fees shall be payable by Asterion Technologies, and Supplier shall immediately transition all data at no additional charge."""
    })

    # 6. Information Security Policies (2025 vs 2026)
    docs.append({
        "title": "Information Security Policy 2026",
        "filename": "infosec_policy_2026.md",
        "document_type": "policy",
        "department": "Information Security",
        "version": "5.0",
        "effective_date": "2026-01-01",
        "confidentiality": "internal",
        "content": """# Information Security Policy 2026
Document ID: AST-SEC-POL-2026-001
Effective Date: January 1, 2026

## 1. Password and Authentication Requirements
- Minimum password length is sixteen (16) characters.
- Passwords must contain upper, lower, numerical, and special characters.
- Multi-factor authentication (MFA) is mandatory across all systems using hardware tokens or authenticator apps; SMS-based MFA is strictly prohibited.
- Passwords expire after 180 days (or continuous zero-trust risk-based reauthentication).

## 2. Data Retention and Destruction Procedures
All customer transactional records must be retained for seven (7) years following account termination, after which they must undergo cryptographic erasure per NIST SP 800-88 standards.

## 3. Incident Reporting Windows
All potential security breaches, unauthorized access attempts, or ransomware detections must be reported to the SOC within sixty (60) minutes of discovery."""
    })

    docs.append({
        "title": "Information Security Policy 2025",
        "filename": "infosec_policy_2025.md",
        "document_type": "policy",
        "department": "Information Security",
        "version": "4.0",
        "effective_date": "2025-01-01",
        "confidentiality": "internal",
        "content": """# Information Security Policy 2025 (SUPERSEDED)
Document ID: AST-SEC-POL-2025-001

## 1. Password Requirements
In 2025, the minimum password length was twelve (12) characters, and SMS MFA was temporarily permitted.

## 2. Incident Reporting
Incident reporting window was four (4) hours in 2025 instead of 60 minutes."""
    })

    # 7. Data Retention Policy 2026
    docs.append({
        "title": "Data Retention Policy 2026",
        "filename": "data_retention_policy_2026.md",
        "document_type": "policy",
        "department": "Compliance",
        "version": "2.0",
        "effective_date": "2026-01-01",
        "confidentiality": "internal",
        "content": """# Global Data Retention and Disposal Policy 2026
Document ID: AST-CMP-POL-2026-005

## 1. Statutory Retention Schedules
- Financial and Accounting Records: Retain for 7 years.
- Employee Personnel Files: Retain for 5 years post-separation.
- Customer Cloud Audit Logs: Retain for 365 days in hot storage, 3 years in cold archive.
- Intellectual Property and Patents: Permanent retention."""
    })

    # 8. Expiring contract: Apex Logistics
    docs.append({
        "title": "Apex Logistics Service Contract",
        "filename": "apex_logistics_contract.md",
        "document_type": "contract",
        "department": "Legal",
        "version": "1.5",
        "effective_date": "2024-03-15",
        "confidentiality": "confidential",
        "content": """# Logistics Services Agreement: Apex Logistics & Asterion Technologies
Contract ID: AST-CTR-2024-042
Effective Date: March 15, 2024
Expiration Date: April 30, 2026 (Expiring within 90 days)

## Section 3: Term and Renewal
This agreement shall terminate on April 30, 2026. Notice of non-renewal must be delivered forty-five (45) days prior to the expiration date."""
    })

    return docs

def generate_bulk_documents(company: Dict[str, Any], count: int, starting_index: int = 1) -> List[Dict[str, Any]]:
    """Generate realistic operational documents across departments to reach 60 docs per company."""
    docs = []
    comp_name = company["name"]
    slug = company["slug"].upper()
    depts = company["departments"]

    doc_types = ["policy", "sop", "report", "handbook", "manual", "contract", "audit"]
    topics = [
        ("Disciplinary and Grievance Procedure", "HR", "policy"),
        ("Employee Onboarding Standard Operating Procedure", "HR", "sop"),
        ("Travel and Expense Booking Guidelines", "HR", "policy"),
        ("Diversity Equity and Inclusion Charter", "HR", "handbook"),
        ("Workplace Health and Ergonomics Standard", "HR", "sop"),
        ("Whistleblower and Anti-Retaliation Policy", "Compliance", "policy"),
        ("Vendor Selection and Due Diligence Matrix", "Procurement", "sop"),
        ("Quarterly Procurement Spend Analysis", "Procurement", "report"),
        ("Capital Asset Depreciation Schedule", "Finance", "report"),
        ("Corporate Treasury and Cash Investment Guidelines", "Finance", "policy"),
        ("Business Continuity and Disaster Recovery Plan", "Operations", "manual"),
        ("Quarterly Operational Efficiency Benchmark", "Operations", "report"),
        ("Change Management and Release Verification SOP", "Operations", "sop"),
        ("Data Protection and Privacy Impact Assessment", "Compliance", "audit"),
        ("Annual Corporate Governance and Risk Register", "Compliance", "audit"),
        ("Access Control and Privileged Identity Management", "Information Security", "policy"),
        ("Vulnerability Management and Penetration Testing SOP", "Information Security", "sop"),
        ("Cloud Infrastructure Architecture Blueprint", "Engineering", "manual"),
        ("Software Development Life Cycle and Secure Coding Standard", "Engineering", "sop"),
        ("Customer Service Level Agreement and Escalation Protocol", "Product", "policy"),
        ("Enterprise API Documentation and Rate Limiting Guide", "Product", "manual"),
        ("Non-Disclosure Agreement Standard Terms", "Legal", "contract"),
        ("Intellectual Property Assignment Agreement", "Legal", "contract"),
        ("Facilities Environmental and Waste Management SOP", "Operations", "sop")
    ]

    for i in range(count):
        idx = starting_index + i
        topic_info = topics[i % len(topics)]
        title_base, default_dept, default_type = topic_info
        dept = default_dept if default_dept in depts else depts[0]
        year = random.choice(["2024", "2025", "2026"])
        v_num = f"{random.randint(1, 3)}.{random.randint(0, 5)}"
        conf = random.choice(["internal", "internal", "public", "confidential"])

        title = f"{title_base} {year}"
        filename = f"{title.lower().replace(' ', '_')}.md"

        # Generate realistic multi-section content
        content = f"""# {title}
Organization: {comp_name}
Reference Code: {slug}-{dept[:3].upper()}-{year}-{idx:03d}
Version: {v_num}
Effective Date: {year}-0{random.randint(1, 9)}-01
Classification: {conf.upper()}

## Section 1: Purpose and Objectives
This document establishes authoritative organizational protocols for {comp_name} regarding {title_base.lower()}. 
All employees, contractors, and affiliates within the {dept} department must strictly adhere to the operational principles outlined herein.

## Section 2: Detailed Requirements and Standards
1. Personnel assigned to this functional area must complete mandatory annual compliance review and acknowledge reading this document.
2. Operational tolerances and threshold metrics must be tracked in the primary enterprise ERP system on a weekly cadence.
3. Any procedural variance exceeding 5% from standard operating tolerance requires written notification to the Department Director.
4. Internal controls and quality assurance checks shall be conducted bi-annually by designated internal audit teams.

## Section 3: Roles and Responsibilities
- Department Leadership: Accountable for resource allocation and policy enforcement.
- Operational Staff: Responsible for daily execution according to standard checklists.
- Compliance Reviewers: Empowered to inspect operational logs and flag exceptions.

## Section 4: Document Governance and Historical Versioning
This procedure is subject to annual review by the {dept} governance council. Superseded versions must be archived in compliance with the corporate data retention standard."""

        docs.append({
            "title": title,
            "filename": filename,
            "document_type": default_type,
            "department": dept,
            "version": v_num,
            "effective_date": f"{year}-01-15",
            "confidentiality": conf,
            "content": content
        })

    return docs

def generate_all_seed_data():
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    all_metadata: List[Dict[str, Any]] = []

    for comp in COMPANIES:
        comp_slug = comp["slug"]
        comp_dir = SEED_DIR / comp_slug
        comp_dir.mkdir(parents=True, exist_ok=True)

        company_docs: List[Dict[str, Any]] = []

        if comp_slug == "asterion":
            # Core 12 connected docs
            core = generate_asterion_core_docs()
            company_docs.extend(core)
            # 48 bulk docs to reach exactly 60
            bulk = generate_bulk_documents(comp, count=48, starting_index=13)
            company_docs.extend(bulk)
        else:
            # 60 docs for Northstar / Meridian
            company_docs = generate_bulk_documents(comp, count=60, starting_index=1)

        # Write files and record metadata
        for doc in company_docs:
            file_path = comp_dir / doc["filename"]
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(doc["content"])

            meta_entry = {
                "company_slug": comp_slug,
                "company_name": comp["name"],
                "title": doc["title"],
                "filename": doc["filename"],
                "relative_path": f"{comp_slug}/{doc['filename']}",
                "document_type": doc["document_type"],
                "department": doc["department"],
                "version": doc["version"],
                "effective_date": doc["effective_date"],
                "confidentiality": doc["confidentiality"]
            }
            all_metadata.append(meta_entry)

    meta_file = SEED_DIR / "metadata.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(all_metadata, f, indent=2)

    print(f"Generated {len(all_metadata)} total documents across {len(COMPANIES)} companies into {SEED_DIR}.")

if __name__ == "__main__":
    generate_all_seed_data()

