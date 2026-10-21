from dataclasses import dataclass, field

from core.enums import Stat
from core.items.base import Attack, Defense


@dataclass(frozen=True)
class Enemy:
    """Définition statique d'un ennemi, partagée par tous ses exemplaires en combat."""
    id: str
    stats: dict[Stat, int]
    level: int = 1
    xp: int = 0                                       # XP donnée à sa défaite, avant la baisse par niveau
    category: str | None = None
    attack: Attack = field(default_factory=Attack)    # armes naturelles : crocs, griffes...
    defense: Defense | None = None

    def __post_init__(self):
        missing = set(Stat) - set(self.stats)
        if missing:
            raise ValueError(f"Stats manquantes : {sorted(s.name for s in missing)}")
        if self.stats[Stat.HEALTH] <= 0:
            raise ValueError("Invalid health value")
        if any(value < 0 for value in self.stats.values()):
            raise ValueError("Invalid stat value")
        if self.level <= 0:
            raise ValueError("Invalid level")
        if self.xp < 0:
            raise ValueError("Invalid xp")

    @property
    def max_health(self) -> int:
        return self.stats[Stat.HEALTH]

    def get_stat(self, stat: Stat) -> int:
        return self.stats[stat]
