from core.items.base import Item, ItemInstance


class UnknownItem(KeyError):
    pass


class ItemCatalog:
    """Définitions statiques des items, indexées par id."""

    def __init__(self, items: dict[str, Item] | None = None):
        self._items: dict[str, Item] = dict(items or {})

    def __contains__(self, item_id: str) -> bool:
        return item_id in self._items

    def __len__(self) -> int:
        return len(self._items)

    def get(self, item_id: str) -> Item:
        try:
            return self._items[item_id]
        except KeyError:
            raise UnknownItem(item_id) from None

    def categories(self) -> list[str]:
        return sorted({i.category for i in self._items.values() if i.category})

    def by_category(self, category: str) -> list[Item]:
        return [i for i in self._items.values() if i.category == category]

    def create(self, item_id: str) -> ItemInstance:
        """Crée un nouvel exemplaire avec son état initial."""
        item = self.get(item_id)
        wear = 1.0 if item.has_state else None
        return ItemInstance(item_id=item.id, wear=wear)
