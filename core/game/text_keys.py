from core.world.models import RoomRef


def zone_key(zone_id: str, field: str) -> str:
    return f"text.{zone_id}.{field}"


def room_key(ref: RoomRef, field: str) -> str:
    return f"text.{ref.zone_id}.rooms.{ref.room_id}.{field}"