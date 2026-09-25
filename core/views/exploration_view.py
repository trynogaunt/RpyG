from dataclasses import dataclass
from .base_view import BaseView
from core.enums import Direction

@dataclass(frozen=True)
class ExplorationView(BaseView):
    zone_name: str
    room_name: str
    room_desc: str
    can_move: dict[Direction, bool]