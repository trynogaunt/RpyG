from dataclasses import dataclass
from core.enums import Screens

@dataclass(frozen=True)
class GameResponse:
    """Represents a response from the game to the player."""
    message: str = ""
    success: bool = True
    screen: Screens | None = None

