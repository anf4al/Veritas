from typing import List, Dict, Any

SEED_EVALUATION_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "eval-1",
        "question": "What is the current WFH policy?",
        "expected_titles": ["Work From Home Policy 2026", "Employee Handbook 2026"],
        "required_permission": "knowledge.search",
        "category": "HR"
    },
    {
        "id": "eval-2",
        "question": "How many annual leave days can an employee carry forward?",
        "expected_titles": ["Leave Policy 2026", "Employee Handbook 2026"],
        "required_permission": "knowledge.search",
        "category": "HR"
    },
    {
        "id": "eval-3",
        "question": "What changed between the 2025 and 2026 procurement policies?",
        "expected_titles": ["Procurement Policy 2025", "Procurement Policy 2026"],
        "required_permission": "knowledge.search",
        "category": "Procurement"
    },
    {
        "id": "eval-4",
        "question": "Which suppliers violated their SLA more than twice?",
        "expected_titles": ["Vendor Performance Report Q4 2025", "Supplier SLA Compliance Review 2026"],
        "required_permission": "knowledge.search",
        "category": "Operations"
    },
    {
        "id": "eval-5",
        "question": "Why was Vendor Atlas classified as high risk?",
        "expected_titles": ["Vendor Atlas Risk Assessment 2026", "Vendor Performance Report Q4 2025"],
        "required_permission": "knowledge.search",
        "category": "Procurement"
    },
    {
        "id": "eval-6",
        "question": "Does the current Vendor Atlas contract permit termination for repeated SLA violations?",
        "expected_titles": ["Vendor Atlas Master Services Agreement", "Procurement Policy 2026"],
        "required_permission": "knowledge.search",
        "category": "Legal"
    },
    {
        "id": "eval-7",
        "question": "Which information-security procedures changed between 2025 and 2026?",
        "expected_titles": ["Information Security Policy 2025", "Information Security Policy 2026"],
        "required_permission": "knowledge.search",
        "category": "Security"
    },
    {
        "id": "eval-8",
        "question": "Which contracts expire within 90 days?",
        "expected_titles": ["Vendor Atlas Master Services Agreement", "Apex Logistics Service Contract"],
        "required_permission": "knowledge.search",
        "category": "Legal"
    },
    {
        "id": "eval-9",
        "question": "Which policies mention data retention?",
        "expected_titles": ["Data Retention Policy 2026", "Information Security Policy 2026", "Compliance and Audit Policy 2026"],
        "required_permission": "knowledge.search",
        "category": "Compliance"
    },
    {
        "id": "eval-10",
        "question": "Compare the current reimbursement policy with the previous version.",
        "expected_titles": ["Reimbursement Policy 2025", "Reimbursement Policy 2026"],
        "required_permission": "knowledge.search",
        "category": "HR"
    }
]
