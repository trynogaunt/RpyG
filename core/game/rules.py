from dataclasses import dataclass
from core.enums import Stat

@dataclass(frozen=True)
class StatRule:
    base: int
    per_point: int
    growth_per_level: int = 1

CREATION_POINTS: int = 10

# Équipement proposé à la création, dans l'ordre d'affichage. Le premier est présélectionné.
STARTER_WEAPONS: tuple[str, ...] = ("wooden_sword", "wooden_shield")

# XP totale à atteindre pour chaque niveau : LEVEL_XP[n - 1] pour le niveau n. Le dernier palier est le niveau max.
LEVEL_XP: tuple[int, ...] = (0, 20, 50, 100, 170, 260, 380, 530, 720, 950)

# Chaque niveau d'avance sur un ennemi retire 30 % de son XP, sans descendre sous 10 % :
# farmer des ennemis faibles s'essouffle et pousse à avancer.
XP_FALLOFF_PER_LEVEL = 0.3
XP_FALLOFF_FLOOR = 0.1

STAT_RULES: dict[Stat, StatRule] = {
    Stat.HEALTH: StatRule(base=10, per_point=5, growth_per_level=5),
    Stat.STRENGTH: StatRule(base=5, per_point=1),
    Stat.SPEED: StatRule(base=5, per_point=1),
    Stat.LUCK: StatRule(base=1, per_point=1),
}