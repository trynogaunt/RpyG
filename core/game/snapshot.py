from dataclasses import dataclass
from core.enums import Stat
from core.world.models import EncounterRef, RoomRef, WorldState
from core.items.base import ItemInstance, Slot

@dataclass(frozen=True)
class PlayerSnapshot:
    name: str
    health: int
    level: int
    allocated_points: tuple[tuple[Stat, int], ...]
    bag: tuple["BagEntry", ...] = ()
    equipped: tuple["EquippedEntry", ...] = ()
    xp: int = 0

@dataclass(frozen=True)
class BagEntry:
    index: int
    instance: ItemInstance
    quantity: int

@dataclass(frozen=True)
class EquippedEntry:
    slots: tuple[Slot, ...]
    instance: ItemInstance

@dataclass(frozen=True)
class GameSnapshot:
    player: PlayerSnapshot
    location: RoomRef
    explored: tuple[RoomRef, ...]
    defeated: tuple[EncounterRef, ...] = ()