from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_verify_endpoint_python():
    payload = {
        "language": "python",
        "version": "3.12",
        "code": "print(42)"
    }
    response = client.post("/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "passed"
    assert "42" in data["stdout"]

def test_verify_endpoint_java():
    payload = {
        "language": "java",
        "version": "21",
        "code": "public class Main{public static void main(String[] a){System.out.println(42);}}"
    }
    response = client.post("/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "passed"

def test_get_decks_list():
    response = client.get("/decks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # At least sample deck d_001 is seeded
    deck_ids = [d["deck_id"] for d in data]
    assert "d_001" in deck_ids

def test_get_deck_by_id():
    response = client.get("/decks/d_001")
    assert response.status_code == 200
    data = response.json()
    assert data["deck_id"] == "d_001"
    assert len(data["slides"]) > 0

def test_regenerate_single_slide():
    response = client.post("/decks/d_001/slides/s_003/regenerate", json={"prompt_hint": "Refined error handling"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "regenerated"
    assert data["slide"]["id"] == "s_003"

def test_framework_upgrade():
    payload = {
        "target_stack": {"java": "21", "spring_boot": "3.3"}
    }
    response = client.post("/decks/d_001/upgrade", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "upgrade_completed"
    assert data["new_stack"]["spring_boot"] == "3.3"

def test_get_report():
    response = client.get("/decks/d_001/report")
    assert response.status_code == 200
    data = response.json()
    assert data["deck_id"] == "d_001"
    assert data["passed"] >= 1

def test_export_pptx():
    response = client.get("/decks/d_001/export?format=pptx")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    assert len(response.content) > 1000

def test_get_deck_notes():
    response = client.get("/decks/d_001/notes")
    assert response.status_code == 200
    data = response.json()
    assert data["deck_id"] == "d_001"
    assert "trainer_notes" in data
    assert "student_notes" in data
    assert len(data["trainer_notes"]) > 0
    assert data["organization"] == "TechSummitTrainers"
