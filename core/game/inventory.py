from dataclasses import dataclass
from core.items.base import Item, Slot, ItemInstance


class InventoryError(Exception):
    pass

class InventoryFull(InventoryError):
    pass

class NotEquippable(InventoryError):
    pass


@dataclass
class InventoryCase:
    instance: ItemInstance | None = None
    quantity: int = 0

    @property
    def item_id(self) -> str | None:
        return self.instance.item_id if self.instance else None

    @property
    def is_empty(self) -> bool:
        return self.instance is None

    def clear(self) -> None:
        self.instance = None
        self.quantity = 0

@dataclass(frozen=True)
class Equipped:
    """Un exemplaire porté, qui peut occuper plusieurs slots (arme à deux mains...)."""
    slots: tuple[Slot, ...]
    instance: ItemInstance

@dataclass(frozen=True)
class SlotCase:
    slot: Slot
    instance: ItemInstance | None = None

    @property
    def item_id(self) -> str | None:
        return self.instance.item_id if self.instance else None

    @property
    def is_empty(self) -> bool:
        return self.instance is None

class Inventory:
    def __init__(self, size: int = 20):
        self.cases: list[InventoryCase] = [InventoryCase() for _ in range(size)]
        self.equipped: list[Equipped] = []

    @property
    def size(self) -> int:
        return len(self.cases)

    @property
    def is_full(self) -> bool:
        return all(not case.is_empty for case in self.cases)

    @property
    def equipment(self) -> list[SlotCase]:
        return [SlotCase(slot=s, instance=e.instance if (e := self.occupant(s)) else None) for s in Slot]

    def occupant(self, slot: Slot) -> Equipped | None:
        return next((e for e in self.equipped if slot in e.slots), None)

    def _empty_cases(self) -> list[InventoryCase]:
        return [case for case in self.cases if case.is_empty]

    def add(self, item: Item, quantity: int = 1, instance: ItemInstance | None = None) -> int:
        if quantity <= 0:
            raise ValueError("quantity doit être > 0")
        instance = instance or ItemInstance(item.id)
        if instance.item_id != item.id:
            raise ValueError(f"L'instance {instance.item_id!r} ne correspond pas à l'item {item.id!r}")
        if instance.wear is not None and item.max_stack > 1:
            raise ValueError("Un exemplaire avec un état ne peut pas être empilé")

        for c in [case for case in self.cases if case.instance == instance and case.quantity < item.max_stack]:
            available_space = item.max_stack - c.quantity
            if quantity <= available_space:
                c.quantity += quantity
                return 0
            else:
                c.quantity += available_space
                quantity -= available_space

        for c in self._empty_cases():
            if quantity <= item.max_stack:
                c.instance = instance
                c.quantity = quantity
                return 0
            else:
                c.instance = instance
                c.quantity = item.max_stack
                quantity -= item.max_stack

        return quantity

    def remove(self, item: Item, quantity: int = 1) -> int:
        if quantity <= 0:
            raise ValueError("quantity doit être > 0")

        for c in [case for case in self.cases[::-1] if case.item_id == item.id]:
            if quantity <= c.quantity:
                c.quantity -= quantity
                if c.quantity == 0:
                    c.clear()
                return 0
            else:
                quantity -= c.quantity
                c.clear()

        return quantity

    def take(self, index: int, quantity: int = 1) -> ItemInstance:
        """Retire `quantity` exemplaires de la case `index` et renvoie leur instance."""
        if quantity <= 0:
            raise ValueError("quantity doit être > 0")
        case = self._case(index)
        if case.quantity < quantity:
            raise InventoryError(f"Case {index} : quantité insuffisante")
        instance = case.instance
        case.quantity -= quantity
        if case.quantity == 0:
            case.clear()
        return instance

    def equip(self, index: int, item: Item, slots: tuple[Slot, ...] | None = None) -> None:
        """Équipe l'item de la case `index`. Les items déjà portés sur ces slots retournent dans le sac."""
        case = self._case(index)
        if case.item_id != item.id:
            raise ValueError(f"La case {index} ne contient pas {item.id!r}")
        if not item.equippable:
            raise NotEquippable(item.id)
        if slots is not None and slots not in item.slots:
            raise NotEquippable(f"{item.id} ne peut pas aller sur {slots}")

        candidates = [slots] if slots is not None else list(item.slots)
        chosen = next((c for c in candidates if all(self.occupant(s) is None for s in c)), candidates[0])

        displaced = []
        for s in chosen:
            e = self.occupant(s)
            if e is not None and e not in displaced:
                displaced.append(e)

        free = len(self._empty_cases()) + (1 if case.quantity == 1 else 0)
        if len(displaced) > free:
            raise InventoryFull()

        instance = self.take(index)
        for e in displaced:
            self.equipped.remove(e)
            self._place(e.instance, prefer=index)
        self.equipped.append(Equipped(slots=chosen, instance=instance))

    def unequip(self, slot: Slot) -> None:
        e = self.occupant(slot)
        if e is None:
            raise InventoryError(f"Rien d'équipé sur {slot.name}")
        if not self._empty_cases():
            raise InventoryFull()
        self.equipped.remove(e)
        self._place(e.instance)

    def _place(self, instance: ItemInstance, prefer: int | None = None) -> None:
        if prefer is not None and self.cases[prefer].is_empty:
            target = self.cases[prefer]
        else:
            target = self._empty_cases()[0]
        target.instance = instance
        target.quantity = 1

    def _case(self, index: int) -> InventoryCase:
        if not 0 <= index < self.size:
            raise InventoryError(f"Case invalide : {index}")
        case = self.cases[index]
        if case.is_empty:
            raise InventoryError(f"Case vide : {index}")
        return case
