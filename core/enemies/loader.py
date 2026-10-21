import json
from pathlib import Path

from core.enemies.base import Enemy
from core.enemies.catalog import EnemyCatalog
from core.enums import Stat
from core.items.base import Attack, Defense
from core.world.models import World

ENEMIES_FOLDER_PATH = Path(__file__).resolve().parents[2] / "data" / "enemies"


class EnemyLoadError(Exception):
    pass


def load_enemies(folder: Path = ENEMIES_FOLDER_PATH) -> dict[str, Enemy]:
    enemies = {}
    for category_dir in sorted(Path(folder).iterdir()):
        if category_dir.is_dir() and not category_dir.name.startswith("_"):
            for enemy_file in sorted(category_dir.glob("*.json")):
                enemy = load_enemy(enemy_file, category=category_dir.name)
                if enemy.id in enemies:
                    raise EnemyLoadError(f"Duplicate enemy id '{enemy.id}' in {enemy_file}")
                enemies[enemy.id] = enemy
    return enemies


def load_enemy_catalog(folder: Path = ENEMIES_FOLDER_PATH) -> EnemyCatalog:
    return EnemyCatalog(load_enemies(folder))


def load_enemy(enemy_file: Path, category: str | None = None) -> Enemy:
    try:
        with open(enemy_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("category", category)
        data["stats"] = {Stat[name.upper()]: value for name, value in data.get("stats", {}).items()}
        if "attack" in data:
            data["attack"] = Attack(**data["attack"])
        if "defense" in data:
            data["defense"] = Defense(**data["defense"])
        return Enemy(**data)
    except Exception as e:
        raise EnemyLoadError(f"Failed to load enemy from {enemy_file}: {e!r}") from e


def check_world_enemies(world: World, catalog: EnemyCatalog) -> None:
    """Chaque ennemi placé dans une salle doit exister dans le catalogue."""
    for zone in world.zones.values():
        for room_id, room in zone.rooms.items():
            for encounter in room.encounters:
                for enemy_id in encounter.enemies:
                    if enemy_id not in catalog:
                        raise EnemyLoadError(f"Ennemi inconnu '{enemy_id}' dans {zone.id}/{room_id}")
