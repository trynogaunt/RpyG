from dataclasses import dataclass
from core.enums import Stat, Direction

@dataclass(frozen=True)
class Action:
    """Player intention in the game, represented as an action that can be executed."""

@dataclass(frozen=True)
class Quit(Action):
    """Action representing the intention to quit the game."""

@dataclass(frozen=True)
class NewGame(Action):
    """Action representing the intention to start a new game."""

@dataclass(frozen=True)
class Creation(Action):
    """Action representing the intention to enter the creation screen."""

@dataclass(frozen=True)
class SetName(Action):
    """Action representing the intention to set the player's name."""
    name: str

@dataclass(frozen=True)
class AllocatePoints(Action):
    """Action representing the intention to allocate points to the player's attributes."""
    stat: Stat
    delta: int = 1


@dataclass(frozen=True)
class ConfirmCreation(Action):
    """Action representing the intention to confirm the creation of the player's character."""

@dataclass(frozen=True)
class Move(Action):
    """Action representing the intention to move the player in a given direction."""
    direction: Direction

