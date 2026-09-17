from backend.app.auth.permissions import check_document_access

def test_employee_cannot_access_confidential_contracts():
    allowed = check_document_access(
        role="EMPLOYEE",
        doc_department="Legal",
        doc_confidentiality="confidential",
        doc_type="contract",
        title="Vendor Atlas Master Services Agreement"
    )
    assert allowed is False

def test_employee_can_access_general_handbook():
    allowed = check_document_access(
        role="EMPLOYEE",
        doc_department="HR",
        doc_confidentiality="internal",
        doc_type="policy",
        title="Work From Home Policy 2026"
    )
    assert allowed is True

def test_hr_cannot_access_infosec_incidents():
    allowed = check_document_access(
        role="HR_MANAGER",
        doc_department="Information Security",
        doc_confidentiality="confidential",
        doc_type="incident",
        title="Q4 Ransomware Incident Investigation"
    )
    assert allowed is False

def test_security_officer_can_access_infosec():
    allowed = check_document_access(
        role="SECURITY_OFFICER",
        doc_department="Information Security",
        doc_confidentiality="confidential",
        doc_type="policy",
        title="Information Security Policy 2026"
    )
    assert allowed is True

