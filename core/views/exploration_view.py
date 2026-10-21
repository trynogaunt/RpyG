from dataclasses import dataclass
from .base_view import BaseView
from core.game.response import Message
from core.enums import Direction
from core.views.player_summary import PlayerSummary


@dataclass(frozen=True)
class EncounterView:
    id: str
    enemies: tuple[tuple[str, int], ...]     # (id d'ennemi, nombre), dans l'ordre d'apparition


@dataclass(frozen=True)
class ExplorationView(BaseView):
    zone_id: str
    room_id: str
    room_description: str
    can_move: dict[Direction, bool]
    player_summary: PlayerSummary
    encounters: tuple[EncounterView, ...] = ()
