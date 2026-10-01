from dataclasses import dataclass
from core.enums import Stat
from core.world.models import RoomRef, WorldState
from core.game.response import Message

@dataclass(frozen=True)
class PlayerSnapshot:
    name: str
    health: int
    level: int
    allocated_points: tuple[tuple[Stat, int], ...]

@dataclass(frozen=True)
class GameSnapshot:
    player: PlayerSnapshot
    location: RoomRef
    explored: tuple[RoomRef, ...]