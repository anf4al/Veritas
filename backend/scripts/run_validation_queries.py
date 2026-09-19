"""Veritas Enterprise Intelligence Platform - Validation Query Execution Script

Executes and verifies the 7 benchmark enterprise validation queries across tenants and roles:
1. "What is the current WFH policy?" (Asterion, Employee)
2. "How many annual leave days are employees entitled to?" (Asterion, Employee)
3. "What changed between the 2025 and 2026 WFH policies?" (Asterion, HR)
4. "Why was Vendor Atlas classified as high risk?" (Asterion, Ops Manager)
5. "Does our contract with Vendor Atlas allow termination?" (Asterion, Ops Manager)
6. "Why was Vendor Atlas classified as high risk, and does our contract allow termination?" (Asterion, Ops Manager)
7. "Why was Vendor Atlas classified as high risk, and does our contract allow termination?" (Meridian, Compliance Officer)
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.company import Company
from backend.app.agents.orchestrator import AgentOrchestrator

VALIDATION_SCENARIOS = [
    {
        "id": 1,
        "name": "Current WFH Policy",
        "company_slug": "asterion",
        "username": "employee@asterion.demo",
        "query": "What is the current WFH policy?",
        "expected_insufficient": False,
        "required_title_keywords": ["Work From Home", "WFH", "Remote"],
        "forbidden_title_keywords": ["2025"],  # Must NOT retrieve only 2025
        "expected_content_keywords": ["2 days", "Tuesday", "Thursday", "10:00 AM"],
    },
    {
        "id": 2,
        "name": "Annual Leave Entitlement",
        "company_slug": "asterion",
        "username": "employee@asterion.demo",
        "query": "How many annual leave days are employees entitled to?",
        "expected_insufficient": False,
        "required_title_keywords": ["Employee Handbook"],
        "forbidden_title_keywords": [],
        "expected_content_keywords": ["20", "annual leave", "service"],
    },
    {
        "id": 3,
        "name": "WFH Policy Comparison (2025 vs 2026)",
        "company_slug": "asterion",
        "username": "hr@asterion.demo",
        "query": "What changed between the 2025 and 2026 WFH policies?",
        "expected_insufficient": False,
        "required_title_keywords": ["Work From Home", "WFH", "Remote"],
        "requires_multi_version": True,
        "forbidden_title_keywords": [],
        "expected_content_keywords": ["2025", "2026"],
    },
    {
        "id": 4,
        "name": "Vendor Atlas Risk Classification",
        "company_slug": "asterion",
        "username": "ops@asterion.demo",
        "query": "Why was Vendor Atlas classified as high risk?",
        "expected_insufficient": False,
        "required_title_keywords": ["Atlas", "Vendor Risk"],
        "forbidden_title_keywords": [],
        "expected_content_keywords": ["SOC 2", "CVE", "breach"],
    },
    {
        "id": 5,
        "name": "Vendor Atlas Contract Termination",
        "company_slug": "asterion",
        "username": "ops@asterion.demo",
        "query": "Does our contract with Vendor Atlas allow termination?",
        "expected_insufficient": False,
        "required_title_keywords": ["Atlas", "Agreement"],
        "forbidden_title_keywords": [],
        "expected_content_keywords": ["Clause 14", "termination", "30 days"],
    },
    {
        "id": 6,
        "name": "Vendor Atlas Dual-Query (Risk + Termination)",
        "company_slug": "asterion",
        "username": "ops@asterion.demo",
        "query": "Why was Vendor Atlas classified as high risk, and does our contract allow termination?",
        "expected_insufficient": False,
        "required_title_keywords": ["Atlas"],
        "forbidden_title_keywords": [],
        "expected_content_keywords": ["high risk", "termination"],
    },
    {
        "id": 7,
        "name": "Vendor Atlas Meridian Negative Isolation",
        "company_slug": "meridian",
        "username": "compliance@meridian.demo",
        "query": "Why was Vendor Atlas classified as high risk, and does our contract allow termination?",
        "expected_insufficient": True,
        "required_title_keywords": [],
        "forbidden_title_keywords": ["Asterion", "Atlas", "HIPAA", "Meridian"],
        "expected_content_keywords": ["insufficient", "no", "not found"],
    }
]

async def run_scenario(db, scenario: Dict[str, Any]) -> Dict[str, Any]:
    print(f"\n{'='*70}")
    print(f"Executing Scenario {scenario['id']}: {scenario['name']}")
    print(f"Company: {scenario['company_slug']} | User: {scenario['username']}")
    print(f"Query: \"{scenario['query']}\"")
    print(f"{'='*70}")

    company = db.query(Company).filter(Company.slug == scenario["company_slug"]).first()
    if not company:
        raise ValueError(f"Company not found: {scenario['company_slug']}")

    user = db.query(User).filter(User.username == scenario["username"]).first()
    if not user:
        raise ValueError(f"User not found: {scenario['username']}")

    orchestrator = AgentOrchestrator(db=db, user=user, tenant_id=company.id)

    start_time = time.time()
    response = await orchestrator.execute_query(query=scenario["query"])
    elapsed_ms = (time.time() - start_time) * 1000

    citations = response.citations
    answer = response.answer
    is_insufficient = response.insufficient_evidence

    print(f"Execution Latency: {elapsed_ms:.1f} ms")
    print(f"Insufficient Evidence: {is_insufficient}")
    print(f"Citation Count: {len(citations)}")
    for i, c in enumerate(citations, 1):
        print(f"  [{i}] {c.title} (Page {c.page}, Score: {c.relevance_score:.4f})")
    print(f"Answer Snippet:\n{answer[:300]}...")

    # Verification checks
    passed = True
    failure_reasons = []

    if is_insufficient != scenario["expected_insufficient"]:
        passed = False
        failure_reasons.append(
            f"Expected insufficient_evidence={scenario['expected_insufficient']}, got {is_insufficient}"
        )

    if scenario["expected_insufficient"]:
        if len(citations) > 0:
            passed = False
            failure_reasons.append(f"Expected 0 citations for insufficient query, got {len(citations)}")
    else:
        if len(citations) == 0:
            passed = False
            failure_reasons.append("Expected citations, got 0")

        # Check required title keywords
        matched_any = any(
            any(kw.lower() in c.title.lower() for kw in scenario["required_title_keywords"])
            for c in citations
        )
        if scenario["required_title_keywords"] and not matched_any:
            passed = False
            failure_reasons.append(
                f"None of citations matched required keywords: {scenario['required_title_keywords']}"
            )

        # Multi-version check for scenario 3
        if scenario.get("requires_multi_version"):
            has_2025 = any("2025" in c.title or "2025" in (c.version or "") for c in citations)
            has_2026 = any("2026" in c.title or "2026" in (c.version or "") for c in citations)
            if not (has_2025 and has_2026):
                passed = False
                failure_reasons.append("Scenario 3 requires citations from both 2025 and 2026 versions")

    status_str = "PASS" if passed else "FAIL"
    print(f"Verification: [{status_str}]")
    if not passed:
        for r in failure_reasons:
            print(f"  - ERROR: {r}")

    return {
        "id": scenario["id"],
        "name": scenario["name"],
        "query": scenario["query"],
        "company": scenario["company_slug"],
        "user": scenario["username"],
        "latency_ms": round(elapsed_ms, 2),
        "insufficient_evidence": is_insufficient,
        "citations": [
            {
                "title": c.title,
                "page": c.page,
                "relevance_score": round(c.relevance_score, 4),
                "section": c.section,
                "version": c.version
            } for c in citations
        ],
        "answer": answer,
        "passed": passed,
        "failure_reasons": failure_reasons
    }

async def main():
    db = SessionLocal()
    try:
        results = []
        all_passed = True
        for scenario in VALIDATION_SCENARIOS:
            res = await run_scenario(db, scenario)
            results.append(res)
            if not res["passed"]:
                all_passed = False

        output_path = Path("backend/scripts/validation_results.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print("\n" + "="*70)
        print(f"VALIDATION SUMMARY: {'ALL 7 SCENARIOS PASSED' if all_passed else 'SOME SCENARIOS FAILED'}")
        print(f"Detailed output saved to: {output_path.resolve()}")
        print("="*70)

        if not all_passed:
            sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())

