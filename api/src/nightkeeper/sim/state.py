"""Live game state the simulator mutates and the archetypes read."""

from dataclasses import dataclass, field

from nightkeeper.sim.schema import Side


@dataclass
class GameState:
    t: float = 0.0
    clock: float = 0.0
    period: int = 1
    goals: dict[Side, int] = field(default_factory=lambda: {Side.HOME: 0, Side.AWAY: 0})
    red_cards: dict[Side, int] = field(default_factory=lambda: {Side.HOME: 0, Side.AWAY: 0})

    @property
    def minute(self) -> float:
        return self.clock / 60.0

    def margin(self, side: Side) -> int:
        """Goals ahead (positive) or behind (negative) for ``side``."""
        return self.goals[side] - self.goals[side.opponent]
