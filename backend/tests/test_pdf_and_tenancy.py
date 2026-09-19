import io
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.company import Company
from backend.app.models.document import Document

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_tokens():
    db = SessionLocal()
    # Admin has access to asterion, northstar, meridian
    admin_login = client.post("/api/v1/auth/login", json={
        "username": "admin@veritas.demo",
        "password": "VeritasAdmin!2026"
    }).json()

    # HR has access only to asterion
    hr_login = client.post("/api/v1/auth/login", json={
        "username": "hr@asterion.demo",
        "password": "VeritasHR!2026"
    }).json()

    # Compliance has access only to meridian
    meridian_login = client.post("/api/v1/auth/login", json={
        "username": "compliance@meridian.demo",
        "password": "MeridianCompliance!2026"
    }).json()

    db.close()
    return {
        "admin": admin_login["access_token"],
        "hr": hr_login["access_token"],
        "meridian": meridian_login["access_token"],
        "admin_user": admin_login["user"]
    }

def test_pdf_serving_and_content_type(auth_tokens):
    """Requirement 14 & 15: GET /api/v1/documents/{id}/file streams PDF with correct Content-Type."""
    db = SessionLocal()
    doc = db.query(Document).filter(Document.storage_path.isnot(None)).first()
    assert doc is not None, "At least one document with storage_path must exist"
    doc_id = doc.id
    db.close()

    headers = {"Authorization": f"Bearer {auth_tokens['admin']}"}
    res = client.get(f"/api/v1/documents/{doc_id}/file", headers=headers)
    assert res.status_code == 200
    assert "application/pdf" in res.headers.get("content-type", "")
    assert len(res.content) > 100

def test_pdf_token_query_param(auth_tokens):
    """Requirement 15: PDF serving supports token query parameter for iframe / embedded viewing."""
    db = SessionLocal()
    doc = db.query(Document).filter(Document.storage_path.isnot(None)).first()
    doc_id = doc.id
    db.close()

    res = client.get(f"/api/v1/documents/{doc_id}/file?token={auth_tokens['admin']}")
    assert res.status_code == 200
    assert "application/pdf" in res.headers.get("content-type", "")

def test_unauthorized_cross_tenant_pdf_access(auth_tokens):
    """Requirement 13 & 18: User cannot stream or access PDF belonging to an unauthorized tenant."""
    db = SessionLocal()
    meridian = db.query(Company).filter(Company.slug == "meridian").first()
    meridian_doc = db.query(Document).filter(
        Document.company_id == meridian.id,
        Document.storage_path.isnot(None)
    ).first()
    assert meridian_doc is not None
    doc_id = meridian_doc.id
    db.close()

    # HR user belongs only to Asterion, not Meridian
    hr_headers = {"Authorization": f"Bearer {auth_tokens['hr']}"}
    res = client.get(f"/api/v1/documents/{doc_id}/file", headers=hr_headers)
    assert res.status_code in (403, 404)

def test_pdf_upload_and_storage_persistence(auth_tokens):
    """Requirement 11 & 12: PDF upload persists binary to storage/documents/{company_id}/{doc_id}.pdf
    and sets storage_path in Document model.
    """
    db = SessionLocal()
    asterion = db.query(Company).filter(Company.slug == "asterion").first()
    company_id = asterion.id
    db.close()

    headers = {"Authorization": f"Bearer {auth_tokens['admin']}"}
    fake_pdf_content = b"%PDF-1.4 Mock Upload Test Content for Veritas"
    files = {"file": ("test_policy_upload.pdf", io.BytesIO(fake_pdf_content), "application/pdf")}
    data = {
        "company_id": company_id,
        "title": "Automated Test Policy Upload",
        "department": "HR",
        "document_type": "policy",
        "version": "1.0",
        "confidentiality": "internal"
    }

    res = client.post("/api/v1/documents/upload", headers=headers, data=data, files=files)
    assert res.status_code == 200
    res_data = res.json()
    new_doc_id = res_data["document_id"]

    # Verify database model has storage_path
    db = SessionLocal()
    uploaded_doc = db.query(Document).filter(Document.id == new_doc_id).first()
    assert uploaded_doc is not None
    assert uploaded_doc.storage_path is not None
    assert Path(uploaded_doc.storage_path).exists()
    assert uploaded_doc.company_id == company_id

    # Verify physical file can be retrieved via streaming endpoint
    stream_res = client.get(f"/api/v1/documents/{new_doc_id}/file", headers=headers)
    assert stream_res.status_code == 200
    assert fake_pdf_content in stream_res.content

    # Clean up test uploaded document
    del_res = client.delete(f"/api/v1/documents/{new_doc_id}", headers=headers)
    assert del_res.status_code == 200
    assert not Path(uploaded_doc.storage_path).exists()
    db.close()

def test_unauthorized_company_switch_rejection(auth_tokens):
    """Requirement 18: Switching to an unauthorized company ID is rejected."""
    db = SessionLocal()
    meridian = db.query(Company).filter(Company.slug == "meridian").first()
    db.close()

    # HR user is unauthorized for Meridian
    hr_headers = {"Authorization": f"Bearer {auth_tokens['hr']}"}
    res = client.post("/api/v1/companies/switch", headers=hr_headers, json={"company_id": meridian.id})
    assert res.status_code == 403

