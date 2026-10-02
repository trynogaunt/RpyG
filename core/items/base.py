from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Item:
    id: str
    type: str
    max_stack: int = 99
    effect: str | None = None
    params: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ItemType:
    name: str
    usable: bool = False
    equippable: bool = False
    stackable: bool = True
    validate: Callable[[Item], None] | None = None


ITEM_TYPES: dict[str, ItemType] = {}


def register_item_type(item_type: ItemType) -> ItemType:
    if item_type.name in ITEM_TYPES:
        raise ValueError(f"Item already registered: {item_type.name!r}")
    ITEM_TYPES[item_type.name] = item_type
    return item_type


def get_item_type(name: str) -> ItemType:
    try:
        return ITEM_TYPES[name]
    except KeyError:
        raise ValueError(f"Unknown item type: {name!r}") from None