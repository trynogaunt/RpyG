"""Combat au tour par tour : le joueur contre un groupe d'ennemis."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum, auto
from random import Random

from core.combat.fighters import Combatant, Fighter, PlayerFighter
from core.combat.moves import Strike
from core.combat.resolution import resolve_attack
from core.combat.rewards import xp_gain
from core.enemies.base import Enemy


@dataclass(frozen=True)
class CombatLogEntry:
    attacker: str
    damage: int
    crit: bool = False
    blocked: bool = False
    foe: int = 0          # index dans CombatState.foes de l'ennemi qui frappe ou qui est frappé


class Outcome(Enum):
    ONGOING = auto()
    VICTORY = auto()
    DEFEAT = auto()


@dataclass
class CombatState:
    player: PlayerFighter
    foes: list[Combatant]
    log: list[CombatLogEntry] = field(default_factory=list)

    @classmethod
    def start(cls, player: PlayerFighter, enemies: Sequence[Enemy]) -> CombatState:
        if not enemies:
            raise ValueError("Liste d'ennemis vide")
        return cls(player=player, foes=[Combatant.spawn(e) for e in enemies])

    @property
    def living(self) -> list[Combatant]:
        return [f for f in self.foes if f.alive]

    @property
    def defeated(self) -> bool:
        return all(not f.alive for f in self.foes)

    def xp_reward(self, player_level: int) -> int:
        return sum(xp_gain(f.enemy.xp, f.enemy.level, player_level) for f in self.foes)

    def can_target(self, index: int) -> bool:
        return 0 <= index < len(self.foes) and self.foes[index].alive

    def play_round(self, move: Strike, rng: Random) -> Outcome:
        """Chacun agit une fois, du plus rapide au plus lent ; le joueur gagne les égalités."""
        # Index des ennemis vivants, None pour le joueur : l'index sert au journal
        turn = [None, *(i for i, f in enumerate(self.foes) if f.alive)]
        turn.sort(key=lambda i: (self._fighter(i).speed, i is None), reverse=True)
        for index in turn:
            if index is None:
                self._strike(self.player, self.foes[move.target], "player", move.target, rng)
            elif self.foes[index].alive:                  # tué plus tôt dans ce tour : il ne frappe pas
                self._strike(self.foes[index], self.player, "enemy", index, rng)
            if self.defeated:
                return Outcome.VICTORY
            if not self.player.alive:
                return Outcome.DEFEAT
        return Outcome.ONGOING

    def _fighter(self, index: int | None) -> Fighter:
        return self.player if index is None else self.foes[index]

    def _strike(self, attacker: Fighter, defender: Fighter, side: str, foe: int, rng: Random) -> None:
        for hit in resolve_attack(attacker.strength, attacker.luck, attacker.attack, attacker.wear,
                                  defender.armor, defender.block, rng):
            defender.take_damage(hit.damage)
            self.log.append(CombatLogEntry(attacker=side, damage=hit.damage, crit=hit.crit,
                                           blocked=hit.blocked, foe=foe))
            if not defender.alive:
                return
