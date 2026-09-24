from dataclasses import dataclass, field

from core.enums import Stat
from core.game.rules import STAT_RULES, CREATION_POINTS

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