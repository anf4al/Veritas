import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal, Base, engine
from backend.scripts.seed_database import seed_database

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    seed_database()

def test_login_success_platform_admin():
    response = client.post("/api/v1/auth/login", json={
        "username": "admin@veritas.demo",
        "password": "VeritasAdmin!2026"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "PLATFORM_ADMIN"
    assert "admin.all" in data["user"]["permissions"]
    assert len(data["user"]["companies"]) >= 3

def test_login_success_employee():
    response = client.post("/api/v1/auth/login", json={
        "username": "employee@asterion.demo",
        "password": "VeritasEmployee!2026"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "EMPLOYEE"
    assert "admin.all" not in data["user"]["permissions"]

def test_login_invalid_password():
    response = client.post("/api/v1/auth/login", json={
        "username": "admin@veritas.demo",
        "password": "WrongPassword123!"
    })
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]

def test_demo_accounts_endpoint():
    response = client.get("/api/v1/auth/demo-accounts")
    assert response.status_code == 200
    accounts = response.json()
    assert len(accounts) == 8
    usernames = [a["username"] for a in accounts]
    assert "admin@veritas.demo" in usernames
    assert "hr@asterion.demo" in usernames

