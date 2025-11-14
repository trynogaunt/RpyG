from classes import character
class Hero(character.Character):
    def __init__(self, name, health, strength, luck):
        super().__init__(name, health, strength)

    def is_alive(self):
        '''Check if the hero is alive based on health.'''
        return self.health > 0