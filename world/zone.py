class Zone:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.rooms = []
    
    def add_room(self, room : 'Room'):
        self.rooms.append(room)
        
    def remove_room(self, room : 'Room'):
        self.rooms.remove(room)