from dataclasses import dataclass

from core.game.combat import CombatLogEntry
from core.views.base_view import BaseView
from core.views.player_summary import PlayerSummary


@dataclass(frozen=True)
class CombatView(BaseView):
    enemy_id: str
    enemy_health: int
    enemy_max_health: int
    player_summary: PlayerSummary
    log: tuple[CombatLogEntry, ...] = ()
