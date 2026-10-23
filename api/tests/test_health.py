from fastapi.testclient import TestClient

from fancut import __version__
from fancut.api.app import create_app
from fancut.config import Settings


def test_health_reports_ok_and_version() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__, "environment": "test"}
