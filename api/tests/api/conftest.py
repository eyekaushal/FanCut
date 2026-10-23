from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from fancut.api.app import create_app
from fancut.api.services import Services
from fancut.config import Settings
from fancut.matchday.matchday import Matchday


@pytest.fixture(scope="session")
def client(matchday: Matchday) -> Iterator[TestClient]:
    """One app for the whole session: no model, no .env, so tests never call Azure."""
    settings = Settings(_env_file=None, environment="test", mcp_allowed_hosts=["testserver"])  # type: ignore[call-arg]
    app = create_app(settings, Services(matchday=matchday, model=None))
    with TestClient(app) as test_client:
        yield test_client
