from dataclasses import dataclass
from .base_view import BaseView
from core.enums import Stat

@dataclass(frozen=True)
class CreationView(BaseView):
    name: str 
    stats_values: dict[Stat, int]
    can_confirm: bool 
    can_add: dict[Stat, bool]
    can_remove: dict[Stat, bool]
    points_left: int 