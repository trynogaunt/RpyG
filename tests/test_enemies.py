import json
from pathlib import Path

import pytest

from core.enemies.base import Enemy
from core.enemies.catalog import EnemyCatalog, UnknownEnemy
from core.enemies.loader import EnemyLoadError, check_world_enemies, load_enemies, load_enemy
from core.enums import Stat
from core.items.base import Attack
from core.world.loader import load_world
from core.world.models import RoomRef

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
STATS = {"health": 12, "strength": 3, "speed": 6, "luck": 1}


def write_enemy(folder: Path, data: dict, category: str = "cave") -> Path:
    path = folder / category / f"{data['id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_load_real_enemies():
    enemies = load_enemies(DATA_DIR / "enemies")
    rat = enemies["cave_rat"]
    assert rat.category == "cave"
    assert rat.max_health == 12
    assert rat.get_stat(Stat.SPEED) == 6
    assert rat.attack == Attack(damage_multiplier=1.0, crit_multiplier=1.5, hits=1)


def test_attack_defaults_when_missing(tmp_path):
    path = write_enemy(tmp_path, {"id": "slime", "stats": STATS})
    assert load_enemy(path).attack == Attack()


@pytest.mark.parametrize("stats", [
    {**STATS, "mana": 3},                    # stat inconnue
    {k: v for k, v in STATS.items() if k != "luck"},   # stat manquante
    {**STATS, "health": 0},                  # PV nuls
    {**STATS, "speed": -1},                  # stat négative
], ids=["inconnue", "manquante", "pv-nuls", "negative"])
def test_invalid_stats_are_rejected(tmp_path, stats):
    path = write_enemy(tmp_path, {"id": "bad", "stats": stats})
    with pytest.raises(EnemyLoadError):
        load_enemy(path)


def test_duplicate_ids_are_rejected(tmp_path):
    write_enemy(tmp_path, {"id": "rat", "stats": STATS}, category="cave")
    write_enemy(tmp_path, {"id": "rat", "stats": STATS}, category="forest")
    with pytest.raises(EnemyLoadError):
        load_enemies(tmp_path)


def test_catalog_get_and_unknown():
    rat = Enemy(id="rat", stats={s: 1 for s in Stat})
    catalog = EnemyCatalog({"rat": rat})
    assert catalog.get("rat") is rat
    assert "ghost" not in catalog
    with pytest.raises(UnknownEnemy):
        catalog.get("ghost")


def test_rooms_load_their_enemies():
    world = load_world(DATA_DIR)
    assert world.get_room(RoomRef("flooded_cave", "water_pool")).enemies == ("cave_rat",)
    assert world.get_room(RoomRef("flooded_cave", "entrance")).enemies == ()


def test_world_enemies_must_exist():
    world = load_world(DATA_DIR)
    check_world_enemies(world, EnemyCatalog(load_enemies(DATA_DIR / "enemies")))
    with pytest.raises(EnemyLoadError):
        check_world_enemies(world, EnemyCatalog())
