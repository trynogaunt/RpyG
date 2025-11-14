from classes import character
from ui_console import on_enter_room
class Hero(character.Character):
    def __init__(self, name, health, strength, luck):
        super().__init__(name, health, strength, luck)
        self.current_room = None
        self.visited_rooms = set()

    def change_room(self, new_room, cause="move"):
        if self.current_room != new_room:
            self.current_room = new_room
            on_enter_room(self)
    
    def move(self, direction):
        if self.current_room and direction in self.current_room.exits:
                if self.current_room.exits[direction] == None:
                    return False
                else:
                    self.change_room(self.current_room.exits[direction])
                    return True
        return False

    def is_alive(self):
        '''Check if the hero is alive based on health.'''
        return self.health > 0