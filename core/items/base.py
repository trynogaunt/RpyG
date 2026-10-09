from dataclasses import dataclass
from enum import Enum

class Slot(Enum):
    RIGHT_HAND = "right_hand"
    LEFT_HAND = "left_hand"
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"

@dataclass(frozen=True)
class Attack:
    damage_multiplier: float = 1.0
    crit_multiplier: float = 1.0
    hits: int = 1

    def __post_init__(self):
        if self.damage_multiplier <= 0:
            raise ValueError("Invalid damage multiplier")
        if self.crit_multiplier <= 0:
            raise ValueError("Invalid crit multiplier")
        if self.hits <= 0:
            raise ValueError("Invalid hits value")

@dataclass(frozen=True)
class Defense:
    armor_multiplier: float = 1.0
    magic_resistance: float = 1.0
    block_chance: float = 0.0


@dataclass(frozen=True)
class Item:
    id: str
    max_stack: int = 1
    category: str | None = None
    attack: Attack | None = None
    defense: Defense | None = None
    # Slots format [["slot"]], for multiple slot needed [["slot", "slot²"]] and unique but mutiple choice [["slot"], ["slot"]]
    slots: list[list[Slot]] | None = None

    @property
    def equippable(self) -> bool:
        return bool(self.slots)

    def check_slots(self) -> bool:
        if self.slots is None:
            return True
        return all(isinstance(subslot, Slot) for sublist in self.slots for subslot in sublist)

