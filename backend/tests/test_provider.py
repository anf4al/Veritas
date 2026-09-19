from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import validate_provider_keys

client = TestClient(app)

def test_validate_provider_keys():
    status = validate_provider_keys()
    assert "provider" in status
    assert "configured" in status
    assert "model" in status
    # Must never expose actual keys
    assert "OPENAI_API_KEY" not in status
    assert "GROQ_API_KEY" not in status
    assert "GROK_API_KEY" not in status

def test_provider_status_endpoint():
    login = client.post("/api/v1/auth/login", json={
        "username": "admin@veritas.demo",
        "password": "VeritasAdmin!2026"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/provider/status", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] in ("groq", "openai", "mock", "grok")
    assert "configured" in data

