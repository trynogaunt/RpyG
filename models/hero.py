from models.character import Character
from events.response import DamageResult, ResponseType, GameResponse

class Hero(Character):
    def __init__(self, name, health, strength, luck, speed, gold=0):
        super().__init__(name, health, strength, luck, speed)
        self.current_room = None
        self.current_zone = None
        self.visited_rooms = set()
        self.gold = gold