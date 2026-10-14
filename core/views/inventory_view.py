from dataclasses import dataclass
from .base_view import BaseView
from core.items.base import Slot

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
class InventoryView(BaseView):
    cases: tuple[InventorySlotView, ...]
    equipment: tuple[EquipmentSlotView, ...]
