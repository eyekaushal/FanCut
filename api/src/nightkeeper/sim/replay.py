"""Streams a recorded match as if it were live, at any speed."""

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable, Sequence

from nightkeeper.sim.schema import Event

Sleep = Callable[[float], Awaitable[None]]


class Replayer:
    """Yields events with the real gaps between them divided by ``speed``.

    ``speed=1`` is real time; ``speed=120`` plays 90 minutes in about 45 seconds.
    The sleep function is injectable so tests run instantly.
    """

    def __init__(self, events: Sequence[Event], speed: float = 1.0, sleep: Sleep = asyncio.sleep):
        if not 1.0 <= speed <= 600.0:
            raise ValueError("speed must be between 1 and 600")
        self._events = events
        self._speed = speed
        self._sleep = sleep

    async def stream(self) -> AsyncIterator[Event]:
        previous_t: float | None = None
        for event in self._events:
            if previous_t is not None and event.t > previous_t:
                await self._sleep((event.t - previous_t) / self._speed)
            previous_t = event.t
            yield event
