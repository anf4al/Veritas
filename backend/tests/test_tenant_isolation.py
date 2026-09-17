import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.company import Company

client = TestClient(app)

def test_cross_tenant_access_rejection():
    # Login as Northstar admin
    ns_login = client.post("/api/v1/auth/login", json={
        "username": "admin@northstar.demo",
        "password": "NorthstarAdmin!2026"
    })
    assert ns_login.status_code == 200
    ns_token = ns_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {ns_token}"}

    # Retrieve Asterion company ID
    db = SessionLocal()
    asterion = db.query(Company).filter(Company.slug == "asterion").first()
    assert asterion is not None
    db.close()

    # Attempt to query Asterion documents with Northstar token
    resp = client.get(f"/api/v1/documents?company_id={asterion.id}", headers=headers)
    assert resp.status_code == 403
    assert "Access denied" in resp.json()["detail"]

def test_platform_admin_can_switch_tenant():
    admin_login = client.post("/api/v1/auth/login", json={
        "username": "admin@veritas.demo",
        "password": "VeritasAdmin!2026"
    })
    admin_token = admin_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    db = SessionLocal()
    northstar = db.query(Company).filter(Company.slug == "northstar").first()
    db.close()

    # Switch to Northstar
    resp = client.post("/api/v1/companies/switch", json={"company_id": northstar.id}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    assert resp.json()["active_company_id"] == northstar.id

