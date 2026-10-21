from dataclasses import dataclass

from core.game.combat import CombatLogEntry
from core.views.base_view import BaseView
from core.views.player_summary import PlayerSummary


@dataclass(frozen=True)
class FoeView:
    """Un ennemi du combat, figé au moment de la vue."""
    enemy_id: str
    health: int
    max_health: int
    tag: str = ""          # "A", "B"... quand plusieurs ennemis portent le même id


@dataclass(frozen=True)
class CombatView(BaseView):
    foes: tuple[FoeView, ...]
    player_summary: PlayerSummary
    log: tuple[CombatLogEntry, ...] = ()
