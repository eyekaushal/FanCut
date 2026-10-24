import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from fancut.api import speech as speech_module
from fancut.api.app import create_app
from fancut.api.services import Services
from fancut.api.speech import Speech, ssml
from fancut.config import Settings
from fancut.matchday.matchday import Matchday
from fancut.profile import Language


def test_without_a_key_the_route_says_so(client: TestClient) -> None:
    response = client.post("/speech", json={"text": "Kingsmere City 1-0", "language": "hi"})
    assert response.status_code == 503


def test_ssml_picks_a_voice_per_language_and_escapes_the_text() -> None:
    hindi = ssml("आपका क्लब <Kingsmere> & co", Language.HINDI).decode()
    assert "hi-IN-SwaraNeural" in hindi and "&lt;Kingsmere&gt; &amp; co" in hindi
    assert "en-IN-NeerjaNeural" in ssml("aapka club", Language.HINGLISH).decode()
    assert "en-GB-SoniaNeural" in ssml("your club", Language.ENGLISH).decode()


def test_a_configured_service_speaks_and_remembers(
    matchday: Matchday, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = Settings(  # type: ignore[call-arg]
        _env_file=None, environment="test", speech_region="westus3", speech_key=SecretStr("k")
    )
    calls: list[str] = []

    def fake_synthesize(_settings: Settings, text: str, language: Language) -> bytes:
        calls.append(f"{language.value}:{text}")
        return b"ID3fake-mp3"

    monkeypatch.setattr(speech_module, "synthesize", fake_synthesize)
    assert Speech(settings).configured
    app = create_app(settings, Services(matchday=matchday, model=None))
    with TestClient(app) as client:
        first = client.post("/speech", json={"text": "Cutting to Kingsmere City", "language": "en"})
        again = client.post("/speech", json={"text": "Cutting to Kingsmere City", "language": "en"})
    assert first.status_code == 200
    assert first.headers["content-type"] == "audio/mpeg"
    assert first.content == again.content == b"ID3fake-mp3"
    assert calls == ["en:Cutting to Kingsmere City"]  # the second call came from the cache
