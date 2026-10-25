"""Spoken lines over Azure AI Speech: one neural voice per language, results cached.

The channel's text is already fact-checked; speech only reads it aloud. Without a key
the route answers 503 and the web app simply hides the voice switch.
"""

import asyncio
import hashlib
import urllib.request
from collections import OrderedDict
from xml.sax.saxutils import escape

from fancut.config import Settings
from fancut.profile import Language

# Hinglish is Hindi in Latin script; an Indian English voice reads it naturally,
# where a Hindi voice would spell it out.
VOICES: dict[Language, tuple[str, str]] = {
    Language.ENGLISH: ("en-GB", "en-GB-SoniaNeural"),
    Language.HINDI: ("hi-IN", "hi-IN-SwaraNeural"),
    Language.HINGLISH: ("en-IN", "en-IN-NeerjaNeural"),
}
OUTPUT_FORMAT = "audio-24khz-48kbitrate-mono-mp3"
MEDIA_TYPE = "audio/mpeg"
CACHE_SIZE = 256


def ssml(text: str, language: Language) -> bytes:
    locale, voice = VOICES[language]
    return (
        f"<speak version='1.0' xml:lang='{locale}'>"
        f"<voice name='{voice}'>{escape(text)}</voice></speak>"
    ).encode()


def synthesize(settings: Settings, text: str, language: Language) -> bytes:
    """One blocking call to the Speech REST API; run it off the event loop."""
    assert settings.speech_region and settings.speech_key, "speech is not configured"
    request = urllib.request.Request(
        f"https://{settings.speech_region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml(text, language),
        headers={
            "Ocp-Apim-Subscription-Key": settings.speech_key.get_secret_value(),
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": OUTPUT_FORMAT,
            "User-Agent": "fancut",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as reply:
        return bytes(reply.read())


class Speech:
    """Speaks lines, remembering the most recent ones so a replayed line costs nothing."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._cache: OrderedDict[str, bytes] = OrderedDict()

    @property
    def configured(self) -> bool:
        return self._settings.speech_configured

    async def speak(self, text: str, language: Language) -> bytes:
        key = hashlib.sha1(f"{language.value}\n{text}".encode()).hexdigest()
        cached = self._cache.get(key)
        if cached is not None:
            self._cache.move_to_end(key)
            return cached
        audio = await asyncio.to_thread(synthesize, self._settings, text, language)
        self._cache[key] = audio
        while len(self._cache) > CACHE_SIZE:
            self._cache.popitem(last=False)
        return audio
