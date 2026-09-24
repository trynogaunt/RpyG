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

    def get_room(self, ref: RoomRef) -> Room:
        zone = self.zones.get(ref.zone)
        if not zone:
            raise ValueError(f"Zone '{ref.zone}' not found")
        room = zone.rooms.get(ref.room)
        if not room:
            raise ValueError(f"Room '{ref.room}' not found in zone '{ref.zone}'")
        return room