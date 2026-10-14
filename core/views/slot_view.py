from dataclasses import dataclass
from core.views.base_view import BaseView

@dataclass(frozen=True)
class SlotView(BaseView):
    name: str | None      
    slot: int
    level: int | None
    location: str | None
    saved_at: str | None
    readable: bool = True

@dataclass(frozen=True)
class SlotsView(BaseView):
    slots: tuple[SlotView, ...]
    mode: str
    selected: SlotView | None = None
    confirm_delete: bool = False