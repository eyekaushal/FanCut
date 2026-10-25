import asyncio
import json
import time
from typing import Any

from fastapi.testclient import TestClient

from fancut import __version__
from fancut.api.mcp import build_mcp
from fancut.api.services import Services
from fancut.matchday.matchday import Matchday


def _stream(client: TestClient, profile_id: str, until: int = 15) -> list[dict[str, Any]]:
    channel = client.post(
        "/channels", json={"profile_id": profile_id, "speed": 600, "until_minute": until}
    ).json()
    overlays = []
    with client.stream("GET", channel["stream"]) as response:
        assert response.headers["content-type"].startswith("text/event-stream")
        for line in response.iter_lines():
            if line.startswith("data:"):
                overlays.append(json.loads(line.removeprefix("data:")))
    return overlays


def test_health_reports_version_and_no_model_in_tests(client: TestClient) -> None:
    body = client.get("/health").json()
    assert body == {
        "status": "ok",
        "version": __version__,
        "environment": "test",
        "model": False,
        "speech": False,
    }


def test_matchday_lists_ten_fixtures_and_the_full_table(client: TestClient) -> None:
    body = client.get("/matchday").json()
    assert len(body["fixtures"]) == 10
    assert [row["position"] for row in body["table"]] == list(range(1, 21))


def test_a_plain_language_profile_becomes_a_channel(client: TestClient) -> None:
    compiled = client.post(
        "/profiles/compile", json={"message": "Copperhill City fan, I follow Yusuf Okafor"}
    ).json()
    assert compiled["compiled"]["profile"]["club_id"] == "copperhill"
    overlays = _stream(client, compiled["profile_id"], until=5)
    assert overlays[0]["type"] == "cut"
    assert "copperhill" in json.dumps(overlays[0]["data"]["facts"]).lower()


def test_the_stream_follows_the_overlay_contract(client: TestClient) -> None:
    overlays = _stream(client, "arjun")
    assert all(o["schema_version"] == "overlay.v1" for o in overlays)
    assert [o["seq"] for o in overlays] == list(range(1, len(overlays) + 1))
    assert overlays[0]["type"] == "cut" and overlays[0]["data"]["kind"] == "open"
    assert overlays[-1]["type"] == "end"


def test_every_cut_is_narrated_and_actions_come_only_from_the_match_on_air(
    client: TestClient,
) -> None:
    overlays = _stream(client, "arjun")
    cuts = {o["data"]["decision_id"] for o in overlays if o["type"] == "cut"}
    narrated = {o["data"]["decision_id"] for o in overlays if o["type"] == "narration"}
    assert cuts and cuts == narrated

    on_air = None
    for overlay in overlays:
        if overlay["type"] == "cut" and overlay["data"]["kind"] != "replay":
            on_air = overlay["data"]["match_id"]
        elif overlay["type"] == "action":
            assert overlay["data"]["match_id"] == on_air


def test_every_cut_carries_the_evidence_for_its_choice_and_the_alternatives(
    client: TestClient,
) -> None:
    opening = _stream(client, "arjun", until=3)[0]["data"]
    assert opening["chosen"]["match_id"] == opening["match_id"]
    assert opening["chosen"]["value"] == opening["value"]
    assert "your_club" in opening["chosen"]["reasons"]
    assert len(opening["alternatives"]) == 3
    assert {"match_id", "value", "drama", "stake", "reasons"} <= opening["alternatives"][0].keys()


def test_focus_locks_the_pitch_to_the_fans_match_while_the_director_keeps_cutting(
    client: TestClient,
) -> None:
    channel = client.post(
        "/channels", json={"profile_id": "maya", "speed": 600, "until_minute": 12}
    ).json()
    focus = client.post(f"/channels/{channel['channel_id']}/focus", json={"match_id": "md34-05"})
    assert focus.json() == {"focus": "md34-05"}

    overlays = []
    with client.stream("GET", channel["stream"]) as response:
        for line in response.iter_lines():
            if line.startswith("data:"):
                overlays.append(json.loads(line.removeprefix("data:")))
    focused = [o["data"] for o in overlays if o["type"] == "focus"]
    assert focused and all(f["match_id"] == "md34-05" for f in focused)
    assert focused[0]["ranking"]["match_id"] == "md34-05"
    assert {"value", "drama", "stake", "reasons"} <= focused[0]["ranking"].keys()
    assert len(focused) > 1  # the ranking is refreshed as the matchday moves
    assert all(o["data"]["match_id"] == "md34-05" for o in overlays if o["type"] == "action")
    assert any(o["type"] == "cut" for o in overlays)  # the Director never stopped


def test_focus_refuses_an_unknown_match_and_null_releases_it(client: TestClient) -> None:
    channel = client.post("/channels", json={"profile_id": "maya", "speed": 600}).json()
    url = f"/channels/{channel['channel_id']}/focus"
    assert client.post(url, json={"match_id": "md99-01"}).status_code == 404
    assert client.post(url, json={"match_id": None}).json() == {"focus": None}
    assert client.post("/channels/nope/focus", json={"match_id": None}).status_code == 404


def test_players_numbers_follow_the_match_on_screen(client: TestClient) -> None:
    overlays = _stream(client, "arjun", until=20)
    players = [o for o in overlays if o["type"] == "players"]
    assert players, "the scoreboard tick carries the players' numbers"
    shown = None
    for overlay in overlays:
        if overlay["type"] == "cut" and overlay["data"]["kind"] != "replay":
            shown = overlay["data"]["match_id"]
        elif overlay["type"] == "players":
            assert overlay["data"]["match_id"] == shown
            assert len(overlay["data"]["players"]) == 22
    last = players[-1]["data"]["players"]
    assert any(p["passes"] for p in last) and any(p["carries"] for p in last)
    for p in last:
        assert 0 <= p["pass_difficulty"] <= 1 and p["top_speed_mps"] <= 10.5
        assert p["passes_completed"] <= p["passes"]


def test_the_recap_waits_for_full_time_then_tells_the_fans_day(client: TestClient) -> None:
    channel = client.post("/channels", json={"profile_id": "arjun", "speed": 600}).json()
    url = f"/channels/{channel['channel_id']}/recap"
    assert client.get(url).status_code == 409  # not yet
    with client.stream("GET", channel["stream"]) as response:
        for _ in response.iter_lines():
            pass
    recap = client.get(url).json()
    assert recap["facts"]["fan_club"] == "Kingsmere City"
    assert recap["source"] == "template" and recap["language"] == "hi"
    assert "Kingsmere City" in recap["text"] and recap["text"] == recap["reference"]
    assert client.get(url).json() == recap  # built once
    assert client.get("/channels/nope/recap").status_code == 404


def test_the_audit_trail_records_every_decision_with_its_evidence(client: TestClient) -> None:
    channel = client.post(
        "/channels", json={"profile_id": "maya", "speed": 600, "until_minute": 10}
    ).json()
    with client.stream("GET", channel["stream"]) as response:
        for _ in response.iter_lines():
            pass
    audit = client.get(channel["audit"]).json()
    assert audit["schema_version"] == "audit.v1" and audit["fan"] == "Maya" and audit["ended"]
    assert audit["model_deployment"] is None  # templates spoke: no model in tests
    assert audit["director"]["min_dwell_s"] == 45.0
    assert audit["decisions"]
    for i, entry in enumerate(audit["decisions"]):
        assert entry["decision_id"] == i
        assert entry["chosen"]["match_id"] == entry["match_id"]
        assert entry["facts"]["home_team"] and entry["reference"]
        assert entry["narration"]["source"] == "template"
        assert entry["narration"]["rejected"] == []
    assert (
        audit["decisions"][0]["kind"] == "open"
        and audit["decisions"][0]["previous_match_id"] is None
    )


def test_the_overlay_contract_documents_every_event_type(client: TestClient) -> None:
    body = client.get("/contract/overlay.v1").json()
    assert body["schema_version"] == "overlay.v1"
    assert body["envelope"]["required"] == ["seq", "t", "type", "data"]
    assert [e["type"] for e in body["events"]] == [
        "cut", "narration", "action", "scoreboard", "table", "fantasy", "focus", "players", "end",
    ]  # fmt: skip
    assert all(e["description"] for e in body["events"])


def test_the_evaluation_measures_the_director_and_tallies_the_fact_checker(
    client: TestClient,
) -> None:
    first = client.get("/evaluation").json()
    assert first["status"] in ("measuring", "ready")
    assert first["grounding"]["review"]["false_claims"] == 0
    assert first["grounding"]["live"]["channels"] >= 1  # earlier tests ran channels
    assert first["grounding"]["live"]["template"] == first["grounding"]["live"]["lines"]
    assert first["safety"]["model_deployment"] is None and first["safety"]["controls"]

    deadline = time.monotonic() + 60
    while (body := client.get("/evaluation").json())["status"] != "ready":
        assert time.monotonic() < deadline, "the measurement did not finish"
        time.sleep(0.2)
    director = body["director"]
    assert director["seeds"] == [34] and director["fans"] == ["Arjun", "Maya"]
    assert director["personal_coverage"] == 1.0 and director["early_cuts"] == 0
    assert director["decisive_goals"] > 0 and director["distinctness_min"] >= 0.5
    assert len(director["per_matchday"]) == 2 and body["progress"] == {"done": 1, "total": 1}


def test_unknown_profiles_and_channels_are_404s(client: TestClient) -> None:
    assert client.post("/channels", json={"profile_id": "nobody"}).status_code == 404
    assert client.get("/channels/nope/audit").status_code == 404


def test_the_mcp_endpoint_completes_a_handshake(client: TestClient) -> None:
    response = client.post(
        "/mcp/",
        headers={"Accept": "application/json, text/event-stream"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1"},
            },
        },
    )
    assert response.status_code == 200
    assert "fancut-drama" in response.text


def test_mcp_tools_answer_about_the_matchday(matchday: Matchday) -> None:
    server = build_mcp(Services(matchday=matchday, model=None))

    async def call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        result = await server.call_tool(name, arguments)
        return json.loads(result.content[0].text)  # type: ignore[union-attr]

    overview = asyncio.run(call("matchday_overview", {}))
    assert len(overview["fixtures"]) == 10
    drama = asyncio.run(
        call("match_drama", {"match_id": overview["fixtures"][0]["match_id"], "minute": 60})
    )
    assert 0 <= drama["suspense"] <= 1
    assert abs(sum(drama["win_probability"].values()) - 1) < 1e-9
    ranking = asyncio.run(call("rank_matches", {"fan": "arjun", "minute": 30}))
    values = [r["value"] for r in ranking["ranking"]]
    assert len(values) == 10 and values == sorted(values, reverse=True)
    assert ranking["on_air"] in {f["match_id"] for f in overview["fixtures"]}
