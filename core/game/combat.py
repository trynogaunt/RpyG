"""Combat au tour par tour contre un seul ennemi, et résolution des coups."""
import math
from dataclasses import dataclass, field
from random import Random

from core.enemies.base import Enemy
from core.items.base import Attack

LUCK_RATIO = 0.03       # chaque point de Chance amplifie le crit de l'arme de 3 %
CRIT_CAP = 0.85


@dataclass(frozen=True)
class CombatLogEntry:
    attacker: str          # "player" ou "enemy"
    damage: int
    crit: bool = False


@dataclass
class CombatState:
    """L'exemplaire de l'ennemi affronté : sa définition ne bouge pas, ses PV si."""
    enemy: Enemy
    enemy_health: int
    log: list[CombatLogEntry] = field(default_factory=list)

    @classmethod
    def start(cls, enemy: Enemy) -> "CombatState":
        return cls(enemy=enemy, enemy_health=enemy.max_health)

    @property
    def enemy_defeated(self) -> bool:
        return self.enemy_health <= 0


@dataclass(frozen=True)
class Hit:
    damage: int
    crit: bool


def crit_chance(attack: Attack, wear: float, luck: int) -> float:
    """Le crit vient de l'arme et baisse avec son usure (1.0 = neuve) ; la Chance l'amplifie."""
    chance = attack.crit_chance * wear
    chance *= 1 + luck * LUCK_RATIO
    return min(chance, CRIT_CAP)


def finalize(damage: float) -> int:
    """Seul arrondi du pipeline : à l'entier supérieur, au moins 1 dès qu'il y a des dégâts."""
    if damage <= 0:
        return 0
    return max(1, math.ceil(round(damage, 6)))   # round : 10.000000000000002 ne doit pas devenir 11


def resolve_attack(strength: int, luck: int, attack: Attack, wear: float, rng: Random) -> list[Hit]:
    """Un coup par `hits`, chacun avec son propre jet de critique."""
    chance = crit_chance(attack, wear, luck)
    hits = []
    for _ in range(attack.hits):
        damage = strength * attack.damage_multiplier
        crit = rng.random() < chance
        if crit:
            damage *= attack.crit_multiplier
        hits.append(Hit(damage=finalize(damage), crit=crit))
    return hits
