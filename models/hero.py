from models.character import Character
from events.response import DamageResult, ResponseType, GameResponse

class Hero(Character):
    def __init__(self, name, health, strength, luck, speed, gold=0):
        super().__init__(name, health, strength, luck, speed)
        self.current_room = None
        self.current_zone = None
        self.visited_rooms = set()
        self.active_effects = []
        self.gold = gold

    def is_alive(self):
        '''Check if the hero is alive based on health.'''
        return self.health > 0