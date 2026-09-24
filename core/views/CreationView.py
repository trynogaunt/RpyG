from dataclasses import dataclass
from dataclasses import field

@dataclass(frozen=True)
class CreationView:
    name: str = ""
    stats_values: dict = field(default_factory=dict)
    can_confirm: bool = False
    can_add: dict = field(default_factory=dict)
    can_remove: dict = field(default_factory=dict)
    points_left: int = 0