import pytest

from nightkeeper.sim import Match, Replayer


async def test_replay_preserves_order_and_compresses_time(league: list[Match]) -> None:
    events = league[0].events
    slept: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        slept.append(seconds)

    streamed = [e async for e in Replayer(events, speed=120, sleep=fake_sleep).stream()]

    assert streamed == list(events)
    assert sum(slept) == pytest.approx((events[-1].t - events[0].t) / 120)


@pytest.mark.parametrize("speed", [0.5, 601])
def test_replay_rejects_out_of_range_speed(speed: float) -> None:
    with pytest.raises(ValueError, match="speed"):
        Replayer([], speed=speed)
