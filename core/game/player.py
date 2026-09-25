from core.enums import Stat
from core.game.rules import STAT_RULES

class Player:
    def __init__(self, name: str, allocated_points: dict[Stat, int] | None = None):
        self.name = name
        self.level = 1
        self.location = None

        self.allocated_points = {stat: 0 for stat in STAT_RULES}
        if allocated_points:
            self.allocated_points.update(allocated_points)

        self.health = self.max_health

    
    @property
    def max_health(self) -> int:
        return self.get_stat(Stat.HEALTH)

    def get_stat(self, stat: Stat) -> int:
        rule = STAT_RULES[stat]
        base_stat = rule.base
        stat_per_level = (self.level - 1) * rule.growth_per_level
        stat_per_points = self.allocated_points[stat] * rule.per_point
        return base_stat + stat_per_points + stat_per_level
    