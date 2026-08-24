from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint_includes_trace_id() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["x-trace-id"].startswith("tr_")


def test_identity_requires_authentication() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/me")

    assert response.status_code == 401


def test_identity_uses_server_auth_adapter() -> None:
    with TestClient(create_app()) as client:
        response = client.get(
            "/api/v1/me", headers={"X-User-Id": "user-a", "X-Tenant-Id": "tenant-a"}
        )

    assert response.status_code == 200
    assert response.json()["tenant_id"] == "tenant-a"
