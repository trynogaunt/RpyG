from dataclasses import dataclass
from core.enums import Direction
from dataclasses import field

@dataclass(frozen=True)
class RoomRef:
    zone_id: str
    room_id: str

@dataclass(frozen=True)
class Room:
    name: str
    description: str
    ref: RoomRef
    look_around: str = ""
    exits: dict[Direction, RoomRef] = field(default_factory=dict)


@dataclass(frozen=True)
class Zone:
    id: str
    name: str
    description: str
    entry_room: str
    rooms: dict[str, Room]


@dataclass(frozen=True)
class World:
    start: RoomRef 
    zones: dict[str, Zone] = field(default_factory=dict)

    def get_zone(self, ref: RoomRef) -> Zone:
        zone = self.zones.get(ref.zone_id)
        if not zone:
            raise ValueError(f"Zone '{ref.zone_id}' not found")
        return zone

    def get_room(self, ref: RoomRef) -> Room:
        zone = self.get_zone(ref)
        room = zone.rooms.get(ref.room_id)
        if not room:
            raise ValueError(f"Room '{ref.room_id}' not found in zone '{ref.zone_id}'")
        return room
    
    def exit_from(self, location: RoomRef, direction: Direction) -> RoomRef | None:
        room = self.get_room(location)
        return room.exits.get(direction)