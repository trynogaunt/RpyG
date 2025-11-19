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
        if slot not in self.equipped_items.keys():
            raise ValueError(f"Invalid slot: {slot}")
        if slot not in item.allowed_slots:
            raise ValueError(f"Item cannot be equipped in slot: {slot}")
        if item in self.items:
            self.items.remove(item)
        else:
            raise ValueError(f"Item {item.name} not in inventory.")
        if self.equipped_items[slot] is not None:
            self.unequip_item(slot)

        if item.type == "Weapon" and item.two_handed:
            self.equipped_items["left_hand"] = item
            self.equipped_items["right_hand"] = item
        else:
            self.equipped_items[slot] = item
        
        

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def list_items(self):
        return [item for item in self.items if item is not None] or False
    
    def get_equipped_item(self, slot):
        return self.equipped_items.get(slot, None)
    
    def list_equipped_items(self):
        return [
            (slot, item)
            for slot, item in self.equipped_items.items()
            if item is not None
        ]
    
    def get_equipped_weapons(self):
        weapons = []
        left_item = self.equipped_items.get("left_hand")
        right_item = self.equipped_items.get("right_hand")
        if left_item and left_item.type == "Weapon":
            if left_item.two_handed:
                weapons.append(left_item)
            else:
                weapons.append(left_item)
        if right_item and right_item.type == "Weapon" and right_item is not left_item:
            weapons.append(right_item)
        return weapons
    
    def unequip_item(self, slot):
        item = self.equipped_items.get(slot)
        if item:
            self.add_item(item)
            if item.type == "Weapon" and item.two_handed:
                self.equipped_items["left_hand"] = None
                self.equipped_items["right_hand"] = None
            else:
                self.equipped_items[slot] = None
        