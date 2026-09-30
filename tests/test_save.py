import copy

import pytest
from dataclasses import replace
from core.game.game import Game
from core.errors import InvalidSave
from core.game.snapshot import GameSnapshot, PlayerSnapshot
from core.game.actions import SetName, AllocatePoints, ConfirmCreation, Explore, Move
from core.enums import Stat, Direction
from core.save import codec, storage
from core.save.store import SaveStore


# ---------- Fixtures ----------

@pytest.fixture(autouse=True)
def isolated_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "save_dir", lambda: tmp_path)
    return tmp_path


@pytest.fixture
def progressed_game(game_in_creation):
    g = game_in_creation
    g.handle_action(SetName("Éléonore"))
    g.handle_action(AllocatePoints(Stat.STRENGTH, 1))    # ADAPTE : une allocation par stat
    g.handle_action(ConfirmCreation())
    g.handle_action(Explore())
    g.handle_action(Move(Direction.NORTH))               # ADAPTE : une direction valide dans small_world
    g.handle_action(Explore())
    g.player.level = 2                                   # ADAPTE : si l'attribut est modifiable
    g.player.health = g.player.max_health - 1
    return g

@pytest.fixture
def make_game(small_world):
    def _make(store=None):
        g = Game(world=small_world, store=store)   # même appel que dans la fixture `game`
        g.start()
        return g
    return _make

@pytest.fixture
def game_with_store(progressed_game):
    store = MemoryStore()
    progressed_game.store = store
    return progressed_game, store

@pytest.fixture
def snapshot(progressed_game) -> GameSnapshot:
    return progressed_game.snapshot()


class MemoryStore:
    """Faux store : garde les instantanés en mémoire, sans disque ni JSON."""

    def __init__(self):
        self.slots: dict[int, GameSnapshot] = {}

    def save(self, slot, snap):
        self.slots[slot] = snap

    def load(self, slot):
        try:
            return self.slots[slot]
        except KeyError:
            raise InvalidSave(f"slot {slot} vide")


# ---------- snapshot / restore ----------

def test_snapshot_restore_roundtrip(progressed_game, make_game):  # ADAPTE : make_game = fabrique d'un Game neuf
    snap = progressed_game.snapshot()
    other = make_game()
    other.restore(snap)
    assert other.snapshot() == snap


def test_snapshot_is_deterministic(progressed_game):
    assert progressed_game.snapshot() == progressed_game.snapshot()


def test_restore_unknown_room_raises_and_keeps_state(progressed_game, snapshot):
    before = progressed_game.snapshot()
    bad = replace(snapshot, location=type(snapshot.location)("zone_fantome", "salle_fantome"))  # ADAPTE : constructeur de RoomRef
    with pytest.raises(InvalidSave):
        progressed_game.restore(bad)
    assert progressed_game.snapshot() == before   # état intact après un échec


def test_restore_inconsistent_points_raises(progressed_game, snapshot):
    p = snapshot.player
    stat = p.allocated_points[0][0]
    bad_player = replace(p, allocated_points=((stat, 9999),) + p.allocated_points[1:])
    bad = replace(snapshot, player=bad_player)
    with pytest.raises(InvalidSave):
        progressed_game.restore(bad)


def test_restore_clamps_health_to_max(progressed_game, snapshot):
    bad = replace(snapshot, player=replace(snapshot.player, health=10**6))
    progressed_game.restore(bad)
    assert progressed_game.snapshot().player.health <= progressed_game.player.max_health  # ADAPTE


# ---------- codec ----------

def test_codec_roundtrip(snapshot):
    assert codec.decode(codec.encode(snapshot)) == snapshot


def test_encode_is_json_serializable(snapshot):
    import json
    json.dumps(codec.encode(snapshot))   # ne doit pas lever


def test_encode_writes_version_and_meta(snapshot):
    data = codec.encode(snapshot)
    assert data["version"] == codec.SAVE_VERSION
    assert data["meta"]["name"] == snapshot.player.name
    assert data["meta"]["level"] == snapshot.player.level


def test_encode_sorts_explored(snapshot):
    data = codec.encode(snapshot)
    keys = [(r["zone_id"], r["room_id"]) for r in data["explored"]]
    assert keys == sorted(keys)


def test_decode_missing_version_raises(snapshot):
    data = codec.encode(snapshot)
    del data["version"]
    with pytest.raises(InvalidSave):
        codec.decode(data)


@pytest.mark.parametrize("bad", ["", "1", "1.0.0", "a.b", "1.-2", None, 1.0])
def test_decode_malformed_version_raises(snapshot, bad):
    data = codec.encode(snapshot)
    data["version"] = bad
    with pytest.raises(InvalidSave):
        codec.decode(data)


def test_decode_other_major_raises(snapshot):
    data = codec.encode(snapshot)
    major, _ = codec.parse_version(codec.SAVE_VERSION)
    data["version"] = f"{major + 1}.0"
    with pytest.raises(InvalidSave):
        codec.decode(data)


def test_decode_newer_minor_raises(snapshot):
    data = codec.encode(snapshot)
    major, minor = codec.parse_version(codec.SAVE_VERSION)
    data["version"] = f"{major}.{minor + 1}"
    with pytest.raises(InvalidSave):
        codec.decode(data)


@pytest.mark.parametrize("section", ["player", "location", "explored"])
def test_decode_missing_section_raises(snapshot, section):
    data = codec.encode(snapshot)
    del data[section]
    with pytest.raises(InvalidSave):
        codec.decode(data)


def test_decode_unknown_stat_raises(snapshot):
    data = codec.encode(snapshot)
    data["player"]["allocated_points"] = {"charisme_inexistant": 1}   # ADAPTE : forme de `allocated_points` dans ton codec
    with pytest.raises(InvalidSave):
        codec.decode(data)


# ---------- SaveStore (codec + disque) ----------

def test_store_roundtrip_through_disk(snapshot):
    store = SaveStore()
    store.save(1, snapshot)
    assert store.load(1) == snapshot


def test_store_load_empty_slot_raises():
    with pytest.raises(InvalidSave):
        SaveStore().load(3)

def test_save_game_stores_current_snapshot(game_with_store):
    game, store = game_with_store
    game.save_game(1)
    assert store.slots[1] == game.snapshot()


def test_load_game_restores_state(game_with_store, make_game):
    game, store = game_with_store
    game.save_game(1)
    other = make_game(store=store)
    other.load_game(1)
    assert other.snapshot() == game.snapshot()


def test_load_game_empty_slot_adds_message_and_keeps_state(game_with_store):
    game, _ = game_with_store
    before = game.snapshot()
    game.load_game(7)
    assert game.snapshot() == before
    assert any(m.key == "ui.messages.invalid_save" for m in game._messages)  # ADAPTE : accès aux messages