from fastapi.testclient import TestClient

try:
    from apps.api.main import app
except ImportError:
    from main import app


def test_health():
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    assert r.json().get("status") in ("ok", "healthy")
