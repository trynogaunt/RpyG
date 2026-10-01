from dataclasses import dataclass
from core.enums import Stat

@dataclass
class PlayerSummary:
    name: str
    level: int
    health: int
    max_health: int
    stats: dict[Stat, int]