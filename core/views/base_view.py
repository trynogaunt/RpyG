from dataclasses import dataclass

@dataclass(frozen=True)
class BaseView:
    """Represents a base view for the game's UI."""