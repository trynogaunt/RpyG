from core.items.base import Item, ItemType, register_item_type

def _validate_weapon(item: Item) -> None:
    damage = item.params.get("damage")
    if not isinstance(damage, int) or isinstance(damage, bool) or damage <= 0:
        raise ValueError(f"{item.id} : 'damage' doit être un entier positif")
    if item.effect is not None:
        raise ValueError(f"{item.id} : une arme n'a pas d'effet d'utilisation")

register_item_type(ItemType(
    name="weapon",
    equippable=True,
    stackable=False,
    validate=_validate_weapon,
))