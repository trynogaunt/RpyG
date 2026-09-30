from core.game.snapshot import GameSnapshot, PlayerSnapshot
from core.world.loader import World, RoomRef
from core.game.game import Message
from core.error import InvalidSave

def encode(snapshot: GameSnapshot) -> dict:
    return {
        "player": {
            "name": snapshot.player.name,
            "health": snapshot.player.health,
            "level": snapshot.player.level,
            "allocated": dict(snapshot.player.allocated),
        },
        "location": {
            "zone_id": snapshot.location.zone_id,
            "room_id": snapshot.location.room_id,
        },
        "world_state": snapshot.world_state,  # Assumes WorldState is serializable
        "explored": [
            {"zone_id": r.zone_id, "room_id": r.room_id} for r in snapshot.explored
        ],
        "messages": [
            {"key": m.key, "text": m.text} for m in snapshot.messages
        ],
    }

def decode(data: dict) -> GameSnapshot:
    return GameSnapshot(
        player=PlayerSnapshot(
            name=data["player"]["name"],
            health=data["player"]["health"],
            level=data["player"]["level"],
            allocated=tuple(data["player"]["allocated"].items()),
        ),
        location=RoomRef(
            zone_id=data["location"]["zone_id"],
            room_id=data["location"]["room_id"],
        ),
        world_state=data["world_state"],  # Assumes WorldState is serializable
        explored=tuple(
            RoomRef(zone_id=r["zone_id"], room_id=r["room_id"]) for r in data["explored"]
        ),
        messages=tuple(
            Message(key=m["key"], text=m["text"]) for m in data["messages"]
        ),
    )