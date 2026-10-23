from fastapi.testclient import TestClient

from nightkeeper import __version__
from nightkeeper.api.app import create_app
from nightkeeper.config import Settings


def test_health_reports_ok_and_version() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__, "environment": "test"}
