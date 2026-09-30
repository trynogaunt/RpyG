import json
import os
import tempfile
from pathlib import Path

from platformdirs import user_data_path

from core.errors import InvalidSave

APP_NAME = "rpyg"


def save_dir() -> Path:
    path = user_data_path(APP_NAME) / "saves"
    path.mkdir(parents=True, exist_ok=True)
    return path


def slot_path(slot: int) -> Path:
    return save_dir() / f"slot_{slot}.json"


def write(slot: int, data: dict) -> None:
    """Écriture atomique : fichier temporaire dans le même dossier, puis remplacement."""
    target = slot_path(slot)
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, prefix=f".slot_{slot}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, target)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def read(slot: int) -> dict:
    path = slot_path(slot)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise InvalidSave(f"Aucune sauvegarde dans le slot {slot}") from e
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
        raise InvalidSave(f"Fichier illisible : {path}") from e
    if not isinstance(data, dict):
        raise InvalidSave(f"Contenu inattendu : {path}")
    return data


def slots() -> list[int]:
    """Numéros des slots qui ont un fichier, triés."""
    found = []
    for p in save_dir().glob("slot_*.json"):
        number = p.stem.removeprefix("slot_")
        if number.isdigit():
            found.append(int(number))
    return sorted(found)


def delete(slot: int) -> None:
    slot_path(slot).unlink(missing_ok=True)