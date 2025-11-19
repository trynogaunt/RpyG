from models.character import Character

class Enemy(Character):
    def __init__(self, name, health, strength,luck=0, speed=0, loot=None):
        super().__init__(name, health, strength, luck=luck, speed=speed)
        self.loot = loot if loot is not None else []

