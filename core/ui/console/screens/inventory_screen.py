from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.game.actions import SelectItem

class InventoryScreen(BaseConsoleScreen):
    def draw(self) -> None:
        v = self.view
        c = v.cases
        for i, slot in enumerate(c):
            if slot.item_id is None:
                print(f"Slot {i + 1}: {self.t('inventory.empty')}")
            else:
                print(f"Slot {i + 1}: Item ID = {slot.item_id}, Quantity = {slot.quantity}")
    
    def ask(self):
        v = self.view
        options = []
        options.append((self.t("inventory.select_item"), SelectItem(slot=int(input(self.t("inventory.select_item") + ": ")) - 1)))
        return options