from dataclasses import dataclass
from .base_view import BaseView
from core.items.base import Attack, Defense, Slot

@dataclass(frozen=True)
class InventorySlotView:
    item_id: str | None
    quantity: int
    wear: float | None = None
    equippable: bool = False

@dataclass(frozen=True)
class EquipmentSlotView:
    slot: Slot
    item_id: str | None = None
    wear: float | None = None

@dataclass(frozen=True)
class ItemDetailView:
    """Fiche d'un objet sélectionné, dans le sac (`index`) ou porté (`equipped_on`)."""
    item_id: str
    quantity: int = 1
    wear: float | None = None
    category: str | None = None
    attack: Attack | None = None
    defense: Defense | None = None
    slots: tuple[tuple[Slot, ...], ...] = ()
    index: int | None = None
    equipped_on: tuple[Slot, ...] | None = None

    @property
    def can_equip(self) -> bool:
        return self.index is not None and bool(self.slots)

    @property
    def can_unequip(self) -> bool:
        return self.equipped_on is not None


@dataclass(frozen=True)
class InventoryView(BaseView):
    cases: tuple[InventorySlotView, ...]
    equipment: tuple[EquipmentSlotView, ...]
    selected: ItemDetailView | None = None
