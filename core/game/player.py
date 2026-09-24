from core.enums import Stat
from core.rules import STAT_RULES

class Player:
    def __init__(self, name: str, health: int = 10, strength: int = 0, speed: int = 0, luck: int = 0):
        self.name = name
        self.level = 1
        self.health = health
        self.stats = {
            Stat.HEALTH: health,
            Stat.STRENGTH: strength,
            Stat.SPEED: speed,
            Stat.LUCK: luck,
        }
    
    def get_stat(self, stat: Stat) -> int:
        return self.stats.get(stat, 0)