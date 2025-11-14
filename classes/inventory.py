class Inventory:
    def __init__(self):
        self.equipped_items = {
            "left_hand": None,
            "right_hand": None,
            "torso": None,
            "legs": None,
            "head": None,
            "feet": None
        }
        self.items = []

    def equip_item(self, item, slot):
        if slot in self.equipped_items:
            self.add_item(self.equipped_items[slot])  # Unequip current item
            self.equipped_items[slot] = item # Equip new item
        else:
            raise ValueError("Invalid equipment slot")

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def list_items(self):
        return [item.name for item in self.items if item is not None] or ["Empty"]
    
    def get_equipped_item(self, slot):
        return self.equipped_items.get(slot, None)
    
    def list_equipped_items(self):
        return {slot: item.name if item else "Empty" for slot, item in self.equipped_items.items()}