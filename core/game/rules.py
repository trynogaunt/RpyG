from dataclasses import dataclass
from core.enums import Stat

@dataclass(frozen=True)
class StatRule:
    base: int
    per_point: int
    growth_per_level: int = 1

CREATION_POINTS: int = 10

STAT_RULES: dict[Stat, StatRule] = {
    Stat.HEALTH: StatRule(base=10, per_point=5),
    Stat.STRENGTH: StatRule(base=5, per_point=1),
    Stat.SPEED: StatRule(base=5, per_point=1),
    Stat.LUCK: StatRule(base=1, per_point=1),
}