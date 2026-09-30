# core/save/codec.py
from datetime import datetime

from core.errors import InvalidSave
from core.game.snapshot import GameSnapshot, PlayerSnapshot
from core.enums import Stat
from core.world.models import RoomRef

SAVE_VERSION = "1.0"


def parse_version(raw) -> tuple[int, int]:
    if not isinstance(raw, str):
        raise InvalidSave(f"Version invalide : {raw!r}")
    parts = raw.split(".")
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        raise InvalidSave(f"Version invalide : {raw!r}")
    return int(parts[0]), int(parts[1])


def _ref_to_dict(ref: RoomRef) -> dict:
    return {"zone_id": ref.zone_id, "room_id": ref.room_id}


def _ref_from_dict(data) -> RoomRef:
    try:
        return RoomRef(zone_id=data["zone_id"], room_id=data["room_id"])
    except (KeyError, TypeError) as e:
        raise InvalidSave(f"Référence de salle invalide : {data!r}") from e


def encode(snap: GameSnapshot) -> dict:
    p = snap.player
    return {
        "version": SAVE_VERSION,
        "saved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "meta": {
            "name": p.name,
            "level": p.level,
            "location": snap.location.room_id,
        },
        "player": {
            "name": p.name,
            "level": p.level,
            "health": p.health,
            "allocated_points": {stat.name: value for stat, value in p.allocated_points},
        },
        "location": _ref_to_dict(snap.location),
        "explored": [
            _ref_to_dict(r)
            for r in sorted(snap.explored, key=lambda r: (r.zone_id, r.room_id))
        ],
    }


def decode(data: dict) -> GameSnapshot:
    if not isinstance(data, dict):
        raise InvalidSave("Contenu inattendu")

    major, minor = parse_version(data.get("version"))
    cur_major, cur_minor = parse_version(SAVE_VERSION)
    if major != cur_major:
        raise InvalidSave(f"Version majeure non supportée : {data['version']}")
    if minor > cur_minor:
        raise InvalidSave(f"Sauvegarde créée par une version plus récente : {data['version']}")

    try:
        player = data["player"]
        allocated_points = []
        for stat_name, value in player["allocated_points"].items():
            if stat_name not in Stat.__members__:
                raise InvalidSave(f"Stat inconnue : {stat_name}")
            if not isinstance(value, int) or isinstance(value, bool):
                raise InvalidSave(f"Valeur invalide pour {stat_name}")
            allocated_points.append((Stat[stat_name], value))

        return GameSnapshot(
            player=PlayerSnapshot(
                name=player["name"],
                level=player["level"],
                health=player["health"],
                allocated_points=tuple(sorted(allocated_points, key=lambda kv: kv[0].name)),
            ),
            location=_ref_from_dict(data["location"]),
            explored=tuple(_ref_from_dict(r) for r in data["explored"]),
        )
    except (KeyError, TypeError, AttributeError) as e:
        raise InvalidSave(f"Sauvegarde incomplète ou mal formée : {e!r}") from e