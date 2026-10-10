from dataclasses import dataclass
from core.items.base import Item

@dataclass
class InventoryCase:
    item_id: str | None = None
    quantity: int = 0

    @property
    def is_empty(self) -> bool:
        return self.item_id is None

class Inventory:
    def __init__(self, size: int = 20):
        self.cases: list[InventoryCase] = [InventoryCase() for _ in range(size)]

    @property
    def size(self) -> int:
        return len(self.cases)
    
    @property
    def is_full(self) -> bool:
        return all(not case.is_empty for case in self.cases)
    
    def add(self, item: Item, quantity: int = 1) -> int:
        if quantity <= 0:
            raise ValueError("quantity doit être > 0")
        
        for c in [case for case in self.cases if case.item_id == item.id and case.quantity < item.max_stack]:
            available_space = item.max_stack - c.quantity
            if quantity <= available_space:
                c.quantity += quantity
                return 0
            else:
                c.quantity += available_space
                quantity -= available_space

        for c in [case for case in self.cases if case.is_empty]:
            if quantity <= item.max_stack:
                c.item_id = item.id
                c.quantity = quantity
                return 0
            else:
                c.item_id = item.id
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
                    c.item_id = None
                return 0
            else:
                quantity -= c.quantity
                c.quantity = 0
                c.item_id = None

        return quantity


