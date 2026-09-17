from enum import Enum
from typing import List, Set, Optional

class Permission(str, Enum):
    COMPANY_READ = "company.read"
    COMPANY_SWITCH = "company.switch"
    USER_READ = "user.read"
    USER_MANAGE = "user.manage"
    DOCUMENT_READ = "document.read"
    DOCUMENT_UPLOAD = "document.upload"
    DOCUMENT_DELETE = "document.delete"
    KNOWLEDGE_INDEX = "knowledge.index"
    KNOWLEDGE_SEARCH = "knowledge.search"
    KNOWLEDGE_SEARCH_RESTRICTED = "knowledge.search.restricted"
    OBSERVABILITY_READ = "observability.read"
    EVALUATION_READ = "evaluation.read"
    EVALUATION_RUN = "evaluation.run"
    ADMIN_ALL = "admin.all"

# Mapping roles to permission sets per Part 1
ROLE_PERMISSIONS: dict[str, Set[Permission]] = {
    "PLATFORM_ADMIN": {
        Permission.COMPANY_READ,
        Permission.COMPANY_SWITCH,
        Permission.USER_READ,
        Permission.USER_MANAGE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
        Permission.DOCUMENT_DELETE,
        Permission.KNOWLEDGE_INDEX,
        Permission.KNOWLEDGE_SEARCH,
        Permission.KNOWLEDGE_SEARCH_RESTRICTED,
        Permission.OBSERVABILITY_READ,
        Permission.EVALUATION_READ,
        Permission.EVALUATION_RUN,
        Permission.ADMIN_ALL
    },
    "COMPANY_ADMIN": {
        Permission.COMPANY_READ,
        Permission.USER_READ,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
        Permission.DOCUMENT_DELETE,
        Permission.KNOWLEDGE_INDEX,
        Permission.KNOWLEDGE_SEARCH,
        Permission.KNOWLEDGE_SEARCH_RESTRICTED,
        Permission.OBSERVABILITY_READ,
        Permission.EVALUATION_READ
    },
    "HR_MANAGER": {
        Permission.COMPANY_READ,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
        Permission.KNOWLEDGE_INDEX,
        Permission.KNOWLEDGE_SEARCH
    },
    "OPERATIONS_MANAGER": {
        Permission.COMPANY_READ,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
        Permission.KNOWLEDGE_INDEX,
        Permission.KNOWLEDGE_SEARCH
    },
    "SECURITY_OFFICER": {
        Permission.COMPANY_READ,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
        Permission.KNOWLEDGE_INDEX,
        Permission.KNOWLEDGE_SEARCH,
        Permission.KNOWLEDGE_SEARCH_RESTRICTED,
        Permission.OBSERVABILITY_READ
    },
    "COMPLIANCE_OFFICER": {
        Permission.COMPANY_READ,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
        Permission.KNOWLEDGE_INDEX,
        Permission.KNOWLEDGE_SEARCH,
        Permission.KNOWLEDGE_SEARCH_RESTRICTED,
        Permission.OBSERVABILITY_READ
    },
    "SALES": {
        Permission.COMPANY_READ,
        Permission.DOCUMENT_READ,
        Permission.KNOWLEDGE_SEARCH
    },
    "EMPLOYEE": {
        Permission.COMPANY_READ,
        Permission.DOCUMENT_READ,
        Permission.KNOWLEDGE_SEARCH
    }
}

def get_role_permissions(role: str) -> List[str]:
    """Retrieve list of string permission names for a given role."""
    perms = ROLE_PERMISSIONS.get(role, set())
    return [p.value for p in perms]

def has_permission(role: str, permission: Permission) -> bool:
    """Check if role holds a specific permission."""
    perms = ROLE_PERMISSIONS.get(role, set())
    return Permission.ADMIN_ALL in perms or permission in perms

def check_document_access(role: str, doc_department: str, doc_confidentiality: str, doc_type: str, title: str = "") -> bool:
    """Evaluate granular departmental and confidentiality access per Part 1 specifications:
    - PLATFORM_ADMIN: full access to everything.
    - COMPANY_ADMIN: full access to assigned tenant docs.
    - HR_MANAGER: HR policies, handbooks, leave, SOPs. NO salary-confidential or security incident investigations.
    - OPERATIONS_MANAGER: Procurement, vendors, SLAs, ops reports, products/process docs. NO HR-confidential.
    - SECURITY_OFFICER: InfoSec policies, incidents, compliance, data retention, audits. NO salary records.
    - COMPLIANCE_OFFICER: Compliance, policy, audit, operations. NO salary records.
    - SALES: Product docs, approved pricing, customer-facing. NO HR, salary, security incidents, confidential contracts.
    - EMPLOYEE: General handbook, leave, WFH, reimbursement. NO restricted HR, security incidents, contracts, or management-only reports.
    """
    if role in ("PLATFORM_ADMIN", "COMPANY_ADMIN"):
        return True

    title_lower = title.lower()
    dept_lower = doc_department.lower()
    type_lower = doc_type.lower()
    conf_lower = doc_confidentiality.lower()

    # Rule: Salary-confidential records are strictly restricted from all non-admins except specialized payroll (none in demo)
    if "salary" in title_lower or "compensation" in title_lower or "payroll" in title_lower:
        return False

    if role == "HR_MANAGER":
        # HR manager cannot access security incident investigations or IT security confidential docs
        if dept_lower in ("information security", "security") and (type_lower == "incident" or conf_lower in ("confidential", "restricted")):
            return False
        return True

    if role == "OPERATIONS_MANAGER":
        # Operations cannot access confidential HR records
        if dept_lower == "hr" and conf_lower in ("confidential", "restricted"):
            return False
        return True

    if role == "SECURITY_OFFICER":
        # Security officer can access security, compliance, legal, operations, IT
        return True

    if role == "COMPLIANCE_OFFICER":
        # Compliance officer can access compliance, audits, policies
        return True

    if role == "SALES":
        # Sales cannot access HR, security incidents, or confidential legal contracts
        if dept_lower == "hr":
            return False
        if dept_lower in ("information security", "security") and conf_lower in ("confidential", "restricted"):
            return False
        if type_lower == "contract" and conf_lower in ("confidential", "restricted"):
            return False
        return True

    if role == "EMPLOYEE":
        # Standard employee can only access general employee handbooks, leave, WFH, reimbursement
        if conf_lower in ("confidential", "restricted"):
            return False
        if dept_lower in ("information security", "security") and "incident" in type_lower:
            return False
        if type_lower in ("contract", "audit") and conf_lower != "public":
            return False
        # General employee allows public/internal HR, general product, general operations
        return conf_lower in ("public", "internal")

    return False
