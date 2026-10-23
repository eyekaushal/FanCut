"""Connection check for Azure: ``uv run python -m fancut.check``.

Asks the Foundry model for one word and has Azure AI Speech say one Hindi sentence.
Prints what worked; never prints keys.
"""

import asyncio
import sys
import urllib.error
import urllib.request
from pathlib import Path

from agent_framework import Agent

from fancut.config import Settings, get_settings
from fancut.llm import chat_client

VOICE = "hi-IN-SwaraNeural"
SAMPLE = "फ़ैनकट तैयार है। चलिए मैच देखते हैं।"  # "FanCut is ready. Let's watch the match."
AUDIO_OUT = Path("data/check-voice.mp3")


async def check_llm(settings: Settings) -> str:
    agent = Agent(chat_client(settings), instructions="Answer with exactly one word.")
    response = await agent.run("Reply with the word: ready")
    return response.text.strip()


def check_speech(settings: Settings) -> int:
    assert settings.speech_region and settings.speech_key
    ssml = (
        f"<speak version='1.0' xml:lang='hi-IN'><voice name='{VOICE}'>{SAMPLE}</voice></speak>"
    ).encode()
    request = urllib.request.Request(
        f"https://{settings.speech_region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml,
        headers={
            "Ocp-Apim-Subscription-Key": settings.speech_key.get_secret_value(),
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
            "User-Agent": "fancut",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as reply:
        audio = reply.read()
    AUDIO_OUT.parent.mkdir(parents=True, exist_ok=True)
    AUDIO_OUT.write_bytes(audio)
    return len(audio)


def main() -> None:
    settings = get_settings()
    ok = True

    if settings.llm_configured:
        try:
            print(f"Model ({settings.llm_deployment}): {asyncio.run(check_llm(settings))!r}")
        except Exception as error:  # report any failure plainly; this is a diagnostic
            ok = False
            print(f"Model: FAILED: {type(error).__name__}: {error}")
    else:
        ok = False
        print("Model: not configured (NK_LLM_ENDPOINT / NK_LLM_API_KEY / NK_LLM_DEPLOYMENT)")

    if settings.speech_configured:
        try:
            size = check_speech(settings)
            print(f"Speech ({settings.speech_region}): {size} bytes of Hindi audio -> {AUDIO_OUT}")
        except urllib.error.HTTPError as error:
            ok = False
            print(f"Speech: FAILED: HTTP {error.code} {error.reason}")
        except Exception as error:
            ok = False
            print(f"Speech: FAILED: {type(error).__name__}: {error}")
    else:
        ok = False
        print("Speech: not configured (NK_SPEECH_REGION / NK_SPEECH_KEY)")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
