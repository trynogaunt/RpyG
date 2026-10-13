from dataclasses import dataclass
from .base_view import BaseView
from core.game.response import Message
from core.enums import Direction
from core.views.player_summary import PlayerSummary

@dataclass(frozen=True)
class InventorySlotView:
    item_id: str | None
    quantity: int

@dataclass(frozen=True)
class InventoryView(BaseView):
    cases: tuple[InventorySlotView, ...]