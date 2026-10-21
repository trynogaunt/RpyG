"""Ce qu'un combattant peut faire pendant son tour."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Strike:
    target: int               # index dans CombatState.foes
