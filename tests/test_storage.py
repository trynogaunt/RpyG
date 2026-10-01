import json

import pytest

from core.errors import InvalidSave
from core.save import storage


@pytest.fixture(autouse=True)
def isolated_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "save_dir", lambda: tmp_path)
    return tmp_path


def test_write_then_read_roundtrip():
    data = {"version": "1.0", "player": {"name": "Éléonore", "level": 3}}
    storage.write(1, data)
    assert storage.read(1) == data


def test_write_overwrites_existing_slot():
    storage.write(1, {"a": 1})
    storage.write(1, {"a": 2})
    assert storage.read(1) == {"a": 2}


def test_write_leaves_no_temp_file(isolated_dir):
    storage.write(1, {"a": 1})
    assert [p.name for p in isolated_dir.iterdir()] == ["slot_1.json"]


def test_failed_write_keeps_old_save_and_cleans_temp(isolated_dir, monkeypatch):
    storage.write(1, {"a": "ancienne"})

    def boom(*args, **kwargs):
        raise OSError("disque plein")

    with monkeypatch.context() as m:
        m.setattr(storage.json, "dump", boom)
        with pytest.raises(OSError):
            storage.write(1, {"a": "nouvelle"})

    assert storage.read(1) == {"a": "ancienne"}
    assert [p.name for p in isolated_dir.iterdir()] == ["slot_1.json"]


def test_read_missing_slot_raises_invalid_save():
    with pytest.raises(InvalidSave):
        storage.read(42)


def test_read_malformed_json_raises_invalid_save(isolated_dir):
    (isolated_dir / "slot_1.json").write_text("{pas du json", encoding="utf-8")
    with pytest.raises(InvalidSave):
        storage.read(1)


def test_read_invalid_utf8_raises_invalid_save(isolated_dir):
    (isolated_dir / "slot_1.json").write_bytes(b"\xff\xfe\x00")
    with pytest.raises(InvalidSave):
        storage.read(1)


def test_read_non_dict_raises_invalid_save(isolated_dir):
    (isolated_dir / "slot_1.json").write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    with pytest.raises(InvalidSave):
        storage.read(1)


def test_slots_are_sorted_and_ignore_other_files(isolated_dir):
    for name in ("slot_10.json", "slot_2.json", "slot_1.json",
                 "slot_abc.json", "notes.txt", ".slot_3_x.tmp"):
        (isolated_dir / name).write_text("{}", encoding="utf-8")
    assert storage.slots() == [1, 2, 10]


def test_slots_empty_when_no_saves():
    assert storage.slots() == []


def test_delete_removes_slot():
    storage.write(1, {"a": 1})
    storage.delete(1)
    assert storage.slots() == []


def test_delete_missing_slot_is_silent():
    storage.delete(99)