from classes import character

class Enemy(character.Character):
    def __init__(self, name, health, strength, loot=None):
        super().__init__(name, health, strength)
        self.loot = loot if loot is not None else []

    def is_alive(self):
        '''Check if the enemy is alive based on health.'''
        return self.health > 0