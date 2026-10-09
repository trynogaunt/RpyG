import json
from pathlib import Path

from core.items.base import Item, Slot, Attack, Defense

ITEMS_FOLDER_PATH = Path(__file__).resolve().parents[2] / "data" / "items"


class ItemLoadError(Exception):
    pass

def load_items():
    items = {}
    for category_dir in ITEMS_FOLDER_PATH.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith("_"):
            for item_file in category_dir.glob("*.json"):
                item = load_item(item_file)
                if item.id not in items:
                    items[item.id] = item
    return items

def load_item(item_file: Path) -> Item:
    try:
        with open(item_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["slots"] = tuple(tuple(Slot(s) for s in combo) for combo in data.get("slots", ()))
            if "attack" in data:
                data["attack"] = Attack(**data["attack"])
            if "defense" in data:
                data["defense"] = Defense(**data["defense"])
            item = Item(**data)
            return item
    except Exception as e:
        raise ItemLoadError(f"Failed to load item from {item_file}: {e}")