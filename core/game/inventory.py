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
    
    def add(self, item: Item, quantity: int = 1, case: InventoryCase | None = None) -> bool:
        while quantity > 0 and not self.is_full:
            for icase in self.cases:
                if icase.is_empty:
                    icase.item_id = item.id
                    if quantity > item.max_stack:
                        icase.quantity = item.max_stack
                        quantity -= item.max_stack
                    else:
                        icase.quantity = quantity
                        quantity = 0
            if quantity > 0 and self.is_full:
                return False
        return True


