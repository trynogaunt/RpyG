from dataclasses import dataclass
from enum import Enum

class Slot(Enum):
    RIGHT_HAND = "right_hand"
    LEFT_HAND = "left_hand"
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    RING = "ring"
    AMULET = "amulet"
    BACK = "back"

@dataclass(frozen=True)
class Attack:
    damage_multiplier: float = 1.0
    crit_multiplier: float = 1.0
    hits: int = 1
    crit_chance: float = 0.0          # chance de critique de l'arme neuve, entre 0 et 1

    def __post_init__(self):
        if self.damage_multiplier <= 0:
            raise ValueError("Invalid damage multiplier")
        if not 0 <= self.crit_chance <= 1:
            raise ValueError("Invalid crit chance")
        if self.crit_multiplier <= 0:
            raise ValueError("Invalid crit multiplier")
        if self.hits <= 0:
            raise ValueError("Invalid hits value")

@dataclass(frozen=True)
class Defense:
    armor: int = 0                    # s'additionne sur tout l'équipement porté
    magic_resistance: float = 1.0
    block_chance: float = 0.0

    def __post_init__(self):
        if self.armor < 0:
            raise ValueError("Invalid armor value")
        if not 0 <= self.block_chance <= 1:
            raise ValueError("Invalid block chance")

@dataclass(frozen=True)
class Effect:
    type: str
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Invalid effect value")


@dataclass(frozen=True)
class Item:
    id: str
    max_stack: int = 1
    category: str | None = None
    attack: Attack | None = None
    defense: Defense | None = None
    on_use: tuple[Effect, ...] | None = None
    on_hit: tuple[Effect, ...] | None = None
    equipped: tuple[Effect, ...] | None = None
    # Slots format [["slot"]], for multiple slot needed [["slot", "slot²"]] and unique but mutiple choice [["slot"], ["slot"]]
    slots: tuple[tuple[Slot, ...], ...] | None = None

    @property
    def equippable(self) -> bool:
        return bool(self.slots)
    
    @property
    def usable(self) -> bool:
        return self.on_use is not None

    @property
    def has_on_hit_effect(self) -> bool:
        return self.on_hit is not None

    @property
    def has_equipped_effect(self) -> bool:
        return self.equipped is not None

    @property
    def has_state(self) -> bool:
        """Un exemplaire porte un état propre (usure...) : il n'est jamais empilé."""
        return self.equippable and self.max_stack == 1

    def check_slots(self) -> bool:
        if self.slots is None:
            return True
        return all(isinstance(subslot, Slot) for sublist in self.slots for subslot in sublist)

@dataclass(frozen=True)
class ItemInstance:
    """Un exemplaire concret d'un item. Deux instances égales peuvent s'empiler."""
    item_id: str
    wear: float | None = None

