"""Les participants d'un combat : tout ce qui peut frapper et être frappé."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.combat.resolution import block_chance
from core.enemies.base import Enemy
from core.enums import Stat
from core.game.player import Player
from core.items.base import Attack


class Fighter(Protocol):
    @property
    def alive(self) -> bool: ...
    @property
    def speed(self) -> int: ...
    @property
    def strength(self) -> int: ...
    @property
    def luck(self) -> int: ...
    @property
    def attack(self) -> Attack: ...
    @property
    def wear(self) -> float: ...
    @property
    def armor(self) -> int: ...
    @property
    def block(self) -> float: ...

    def take_damage(self, damage: int) -> None: ...


@dataclass
class Combatant:
    """Un exemplaire d'ennemi en combat : sa définition ne bouge pas, ses PV si."""
    enemy: Enemy
    health: int

    @classmethod
    def spawn(cls, enemy: Enemy) -> Combatant:
        return cls(enemy=enemy, health=enemy.max_health)

    def take_damage(self, damage: int) -> None:
        self.health = max(0, self.health - damage)

    @property
    def alive(self) -> bool:
        return self.health > 0

    @property
    def speed(self) -> int:
        return self.enemy.get_stat(Stat.SPEED)

    @property
    def strength(self) -> int:
        return self.enemy.get_stat(Stat.STRENGTH)

    @property
    def luck(self) -> int:
        return self.enemy.get_stat(Stat.LUCK)

    @property
    def attack(self) -> Attack:
        return self.enemy.attack

    @property
    def wear(self) -> float:
        return 1.0                # pas d'exemplaire d'arme : les armes naturelles sont toujours « neuves »

    @property
    def armor(self) -> int:
        return self.enemy.defense.armor if self.enemy.defense else 0

    @property
    def block(self) -> float:
        defense = self.enemy.defense
        return block_chance(defense.block_chance, 1.0, self.speed, self.luck) if defense else 0.0


@dataclass
class PlayerFighter:
    """Le joueur vu par le combat : son équipement est figé au début, ses PV restent ceux du joueur."""
    player: Player
    attack: Attack
    wear: float
    armor: int
    block: float

    def take_damage(self, damage: int) -> None:
        self.player.health = max(0, self.player.health - damage)

    @property
    def alive(self) -> bool:
        return self.player.health > 0

    @property
    def speed(self) -> int:
        return self.player.get_stat(Stat.SPEED)

    @property
    def strength(self) -> int:
        return self.player.get_stat(Stat.STRENGTH)

    @property
    def luck(self) -> int:
        return self.player.get_stat(Stat.LUCK)
