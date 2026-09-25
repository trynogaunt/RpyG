from dataclasses import dataclass
from .base_view import BaseView
from core.enums import Direction
from core.views.player_summary import PlayerSummary


@dataclass(frozen=True)
class ExplorationView(BaseView):
    zone_name: str
    room_name: str
    room_description: str
    can_move: dict[Direction, bool]
    player_summary: PlayerSummary