from fastapi.testclient import TestClient

from app.config import MAX_HTML_CHARS
from app.main import app
from tests.factories import build_page

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rules_endpoint_lists_all_rules():
    response = client.get("/rules")
    assert response.status_code == 200
    rules = response.json()
    assert len(rules) == 12
    assert sum(r["weight"] for r in rules) == 100
    assert {"id", "description", "severity", "weight"} <= set(rules[0])


def test_analyze_good_page():
    response = client.post("/analyze", json={"html": build_page()})
    assert response.status_code == 200
    body = response.json()
    assert body["score"] == 100
    assert body["grade"] == "A"
    assert body["stats"]["h1_count"] == 1
    assert len(body["findings"]) == 12


def test_analyze_poor_page_reports_failures():
    response = client.post("/analyze", json={"html": "<html><body><p>hi</p></body></html>"})
    assert response.status_code == 200
    body = response.json()
    assert body["score"] < 40
    assert body["failed"] > 0


def test_analyze_rejects_empty_html():
    assert client.post("/analyze", json={"html": ""}).status_code == 422


def test_analyze_rejects_missing_field():
    assert client.post("/analyze", json={}).status_code == 422


def test_analyze_rejects_wrong_type():
    assert client.post("/analyze", json={"html": 123}).status_code == 422


def test_analyze_rejects_oversized_html():
    response = client.post("/analyze", json={"html": "a" * (MAX_HTML_CHARS + 1)})
    assert response.status_code == 422
