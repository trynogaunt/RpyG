from core.enums import Stat
from core.game.rules import LEVEL_XP, STAT_RULES
from core.world.models import RoomRef
from core.views.player_summary import PlayerSummary
from core.game.inventory import Inventory

class Player:
    def __init__(self, name: str, allocated_points: dict[Stat, int] | None = None, location: RoomRef | None = None):
        self.name = name
        self.level = 1
        self.xp = 0                        # XP totale depuis la création, jamais remise à zéro
        self.location: RoomRef | None = location
        self.inventory = Inventory()
        self.golds: int = 0

        self.allocated_points = {stat: 0 for stat in STAT_RULES}
        if allocated_points:
            self.allocated_points.update(allocated_points)

        self.health = self.max_health

    
    @property
    def max_health(self) -> int:
        return self.get_stat(Stat.HEALTH)

    @property
    def xp_next(self) -> int | None:
        """XP totale à atteindre pour le niveau suivant, None au niveau max."""
        return LEVEL_XP[self.level] if self.level < len(LEVEL_XP) else None

    def gain_xp(self, amount: int) -> int:
        """Ajoute l'XP et monte d'autant de niveaux que possible ; renvoie le nombre de niveaux gagnés.

        Les PV max gagnés en montant s'ajoutent aussi aux PV actuels.
        """
        self.xp += amount
        gained = 0
        while self.xp_next is not None and self.xp >= self.xp_next:
            before = self.max_health
            self.level += 1
            self.health += self.max_health - before
            gained += 1
        return gained

    def get_stat(self, stat: Stat) -> int:
        rule = STAT_RULES[stat]
        base_stat = rule.base
        stat_per_level = (self.level - 1) * rule.growth_per_level
        stat_per_points = self.allocated_points[stat] * rule.per_point
        return base_stat + stat_per_points + stat_per_level
    
    def to_summary(self) -> PlayerSummary:


        return PlayerSummary(
            name=self.name,
            level=self.level,
            health=self.health,
            max_health=self.max_health,
            stats={stat: self.get_stat(stat) for stat in STAT_RULES if stat != Stat.HEALTH},
            xp=self.xp,
            xp_next=self.xp_next,
        )

    def add_item_to_inventory(self, item, quantity: int = 1) -> int:
        return self.inventory.add(item, quantity)

    def remove_item_from_inventory(self, item, quantity: int = 1) -> int:
        return self.inventory.remove(item, quantity)
    
    def inventory_contents(self) -> list[tuple[str | None, int]]:
        return [(c.item_id, c.quantity) for c in self.inventory.cases]

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "level": self.level,
            "health": self.health,
            "max_health": self.max_health,
            "allocated_points": self.allocated_points,
            "location": self.location,
            "inventory": self.inventory_contents(),
        }