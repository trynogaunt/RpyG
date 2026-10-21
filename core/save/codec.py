# core/save/codec.py
from datetime import datetime

from core.errors import InvalidSave
from core.game.snapshot import GameSnapshot, PlayerSnapshot, BagEntry, EquippedEntry
from core.enums import Stat
from core.items.base import ItemInstance, Slot
from core.world.models import EncounterRef, RoomRef

SAVE_VERSION = "1.3"


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


def _encounter_to_dict(ref: EncounterRef) -> dict:
    return {**_ref_to_dict(ref.room), "encounter_id": ref.encounter_id}


def _encounter_from_dict(data) -> EncounterRef:
    encounter_id = data.get("encounter_id") if isinstance(data, dict) else None
    if not isinstance(encounter_id, str):
        raise InvalidSave(f"Rencontre invalide : {data!r}")
    return EncounterRef(room=_ref_from_dict(data), encounter_id=encounter_id)


def _instance_to_dict(instance: ItemInstance) -> dict:
    data = {"id": instance.item_id}
    if instance.wear is not None:
        data["wear"] = instance.wear
    return data


def _instance_from_dict(data) -> ItemInstance:
    item_id, wear = data["id"], data.get("wear")
    if not isinstance(item_id, str):
        raise InvalidSave(f"Id d'item invalide : {item_id!r}")
    if wear is not None and (not isinstance(wear, (int, float)) or isinstance(wear, bool)):
        raise InvalidSave(f"Usure invalide : {wear!r}")
    return ItemInstance(item_id=item_id, wear=None if wear is None else float(wear))


def _int(value, what: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise InvalidSave(f"{what} invalide : {value!r}")
    return value


def _slot(value) -> Slot:
    try:
        return Slot(value)
    except ValueError as e:
        raise InvalidSave(f"Slot inconnu : {value!r}") from e


def _inventory_from_dict(data) -> tuple[tuple[BagEntry, ...], tuple[EquippedEntry, ...]]:
    bag = tuple(
        BagEntry(
            index=_int(e["index"], "Index"),
            instance=_instance_from_dict(e),
            quantity=_int(e["quantity"], "Quantité"),
        )
        for e in data.get("bag", [])
    )
    equipped = tuple(
        EquippedEntry(slots=tuple(_slot(s) for s in e["slots"]), instance=_instance_from_dict(e))
        for e in data.get("equipped", [])
    )
    return bag, equipped


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
            "xp": p.xp,
            "health": p.health,
            "allocated_points": {stat.name: value for stat, value in p.allocated_points},
            "inventory": {
                "bag": [
                    {"index": e.index, **_instance_to_dict(e.instance), "quantity": e.quantity}
                    for e in p.bag
                ],
                "equipped": [
                    {"slots": [s.value for s in e.slots], **_instance_to_dict(e.instance)}
                    for e in p.equipped
                ],
            },
        },
        "location": _ref_to_dict(snap.location),
        "explored": [
            _ref_to_dict(r)
            for r in sorted(snap.explored, key=lambda r: (r.zone_id, r.room_id))
        ],
        "defeated": [_encounter_to_dict(d) for d in snap.defeated],
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

        # Absent des sauvegardes 1.0 : inventaire vide
        bag, equipped = _inventory_from_dict(player.get("inventory", {}))

        return GameSnapshot(
            player=PlayerSnapshot(
                name=player["name"],
                level=player["level"],
                health=player["health"],
                allocated_points=tuple(sorted(allocated_points, key=lambda kv: kv[0].name)),
                bag=bag,
                equipped=equipped,
                xp=_int(player.get("xp", 0), "XP"),         # absente avant 1.3
            ),
            location=_ref_from_dict(data["location"]),
            explored=tuple(_ref_from_dict(r) for r in data["explored"]),
            # Absent des sauvegardes 1.0 et 1.1 : aucune rencontre vaincue
            defeated=tuple(_encounter_from_dict(d) for d in data.get("defeated", [])),
        )
    except (KeyError, TypeError, AttributeError) as e:
        raise InvalidSave(f"Sauvegarde incomplète ou mal formée : {e!r}") from e