from dataclasses import dataclass, field

from core.enums import Stat
from core.game.rules import STAT_RULES, CREATION_POINTS
from core.views.creation_view import CreationView

@dataclass
class CreationState:
    name: str = ""
    allocated_points: dict[Stat, int] = field(default_factory=lambda: {stat: 0 for stat in STAT_RULES})

    @property
    def points_left(self) -> int:
        return CREATION_POINTS - sum(self.allocated_points.values())
    
    def can_add(self, stat: Stat) -> bool:
        return self.points_left > 0
    
    def can_remove(self, stat: Stat) -> bool:
        return self.allocated_points[stat] > 0
    
    def can_confirm(self) -> bool:
        return self.name != ""
    
    def stat_value(self, stat: Stat) -> int:
        rule = STAT_RULES[stat]
        return rule.base + self.allocated_points[stat] * rule.per_point
    
    def to_view(self) -> CreationView:

        stats_values = {}
        can_add = {}
        can_remove = {}

        for stat in STAT_RULES:
            stats_values[stat] = self.stat_value(stat)
            can_add[stat] = self.can_add(stat)
            can_remove[stat] = self.can_remove(stat)


        return CreationView(
            name=self.name,
            stats_values=stats_values,
            points_left=self.points_left,
            can_confirm=self.can_confirm(),
            can_add=can_add,
            can_remove=can_remove
        )