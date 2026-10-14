from dataclasses import dataclass, field

from core.enums import Stat
from core.game.rules import STAT_RULES, CREATION_POINTS
from core.views.creation_view import CreationView

@dataclass
class CreationState:
    name: str = ""
    allocated_points: dict[Stat, int] = field(default_factory=lambda: {stat: 0 for stat in STAT_RULES})
    starter_choices: tuple[str, ...] = ()
    starter: str | None = None

    def __post_init__(self):
        if self.starter is None and self.starter_choices:
            self.starter = self.starter_choices[0]

    @property
    def points_left(self) -> int:
        return CREATION_POINTS - sum(self.allocated_points.values())
    
    def can_add(self, stat: Stat) -> bool:
        return self.points_left > 0
    
    def can_remove(self, stat: Stat) -> bool:
        return self.allocated_points[stat] > 0
    
    def can_choose(self, item_id: str) -> bool:
        return item_id in self.starter_choices

    def can_confirm(self) -> bool:
        return self.name != "" and (self.starter is not None or not self.starter_choices)
    
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
            can_remove=can_remove,
            starter_choices=self.starter_choices,
            starter=self.starter,
        )