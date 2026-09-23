from dataclasses import dataclass

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