class Room:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.exits = {"north": None, "south": None, "east": None, "west": None}
        self.items = []
        self.chests = []
        self.enemies = []

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def remove_enemy(self, enemy):
        self.enemies.remove(enemy)
        
    def contain_enemy(self) -> bool:
        if self.enemies:
            return True
        return False

    def __str__(self):
        return f"{self.name}: {self.description}"

def connect(room_a: Room, room_b: Room, direction_a_to_b: str, direction_b_to_a: str):
    room_a.exits[direction_a_to_b] = room_b
    if direction_b_to_a is not None:
        room_b.exits[direction_b_to_a] = room_a

def main():
    room1 = Room("Hall", "A spacious hall with marble floors.")
    room2 = Room("Library", "A quiet library filled with books.")
    connect(room1, room2, "north", "south")
    print(room1)
    print(f"Exits from {room1.name}: {list(key for key in room1.exits if room1.exits[key] is not None)}")
    print(f"Exits from {room2.name}: {list(key for key in room2.exits if room2.exits[key] is not None)}")

if __name__ == "__main__":
    main()