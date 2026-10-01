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
    slots: list[SlotView, ...]
    mode: str