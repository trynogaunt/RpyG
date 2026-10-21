"""Combat au tour par tour contre un seul ennemi, et résolution des coups."""
from __future__ import annotations
import math

from collections.abc import Sequence

from dataclasses import dataclass, field
from random import Random

from core.enemies.base import Enemy
from core.items.base import Attack

LUCK_RATIO = 0.03       
CRIT_CAP = 0.85
ARMOR_SCALE = 100       
BLOCK_CAP = 0.30
BLOCK_SCALE = 20
BLOCK_STAT_BONUS = 2
BLOCK_LUCK_WEIGHT = 0.5


@dataclass(frozen=True)
class CombatLogEntry:
    attacker: str         
    damage: int
    crit: bool = False
    blocked: bool = False
    foe: int = 0          # index dans CombatState.foes de l'ennemi qui frappe ou qui est frappé

@dataclass
class Combatant:
    """Un exemplaire d'ennemi en combat seuls ses PV baissent"""
    enemy: Enemy
    health: int

    @classmethod
    def spawn(cls, enemy: Enemy) -> Combatant:
        return cls(enemy=enemy, health=enemy.max_health)
    
    def take_damage(self, damage) -> None:
        self.health = max(0, self.health - damage)

    @property
    def alive(self) -> bool:
        return not self.health <= 0

@dataclass
class CombatState:
    foes: list[Combatant]
    log: list[CombatLogEntry] = field(default_factory=list)

    @classmethod
    def start(cls, enemy: Sequence[Enemy]) -> CombatState:
        if not enemy:
            raise ValueError("Liste d'ennemie vide")

        enemy_list = []
        for e in enemy:
            comb = Combatant.spawn(e)
            enemy_list.append(comb)
        
        return cls(foes=enemy_list, log=[])
    
    @property
    def living(self) -> list[Combatant]:
        return [f for f in self.foes if f.alive]

    @property
    def defeated(self) -> bool:
        return all(not f.alive for f in self.foes)


@dataclass(frozen=True)
class Hit:
    damage: int
    crit: bool
    blocked: bool = False


def crit_chance(attack: Attack, wear: float, luck: int) -> float:
    """Le crit vient de l'arme et baisse avec son usure (1.0 = neuve) ; la Chance l'amplifie."""
    chance = attack.crit_chance * wear
    chance *= 1 + luck * LUCK_RATIO
    return min(chance, CRIT_CAP)


def block_chance(base: float, wear: float, speed: int, luck: int) -> float:
    """Le blocage vient du bouclier : la Vitesse et la Chance le multiplient, au plus par 3, sans l'atteindre."""
    stat = speed + luck * BLOCK_LUCK_WEIGHT
    chance = base * wear * (1 + BLOCK_STAT_BONUS * stat / (stat + BLOCK_SCALE))
    return min(chance, BLOCK_CAP)


def armor_ratio(armor: int) -> float:
    """Part des dégâts qui passe l'armure : chaque point compte de moins en moins, sans jamais tout bloquer."""
    return ARMOR_SCALE / (ARMOR_SCALE + armor)


def finalize(damage: float, rng: Random) -> int:
    """Seul arrondi du pipeline, stochastique : 2.7 donne 3 dans 70 % des cas, 2 sinon.

    En moyenne on retombe sur la vraie valeur, donc même une petite armure compte.
    Au moins 1 dès qu'il y a des dégâts.
    """
    if damage <= 0:
        return 0
    damage = round(damage, 6)                    # 10.000000000000002 doit rester 10, sans jet
    whole = math.floor(damage)
    fraction = round(damage - whole, 6)          # 2.7 - 2 vaut 0.7000000000000002
    if fraction and rng.random() < fraction:
        whole += 1
    return max(1, whole)


def resolve_attack(strength: int, luck: int, attack: Attack, wear: float, armor: int, block: float,
                   rng: Random) -> list[Hit]:
    """Un coup par `hits` : jet de blocage de la cible, puis de critique, puis réduction par son armure."""
    chance = crit_chance(attack, wear, luck)
    hits = []
    for _ in range(attack.hits):
        if block and rng.random() < block:
            hits.append(Hit(damage=0, crit=False, blocked=True))
            continue
        damage = strength * attack.damage_multiplier
        crit = rng.random() < chance
        if crit:
            damage *= attack.crit_multiplier
        damage *= armor_ratio(armor)
        hits.append(Hit(damage=finalize(damage, rng), crit=crit))
    return hits
