from dataclasses import dataclass, field
from collections.abc import Mapping

@dataclass(frozen=True)
class Item:
    """Class representing an item in the game."""
    id: str
    type: str
    name: str
    description: str
    stackable: bool = True
    max_stack: int = 99
    effect: str | None = None
    params: Mapping[str, any] = field(default_factory=dict)

