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
        if item.type not in ["Weapon", "Armor", "Shield"]:
            raise ValueError("Only weapons and armor can be equipped.")
        
        if item.type in ["Weapon", "Shield"] and slot not in ["left_hand", "right_hand"]:
            raise ValueError("Weapons can only be equipped in left_hand or right_hand slots.")
        
        if item.type == "Armor" and slot not in item.allowed_parts:
            raise ValueError(f"{item.name} cannot be equipped in the {slot} slot.")
        
        left_item = self.equipped_items.get("left_hand")
        right_item = self.equipped_items.get("right_hand")

        if item.type in ["Weapon", "Shield"] and item.two_handed: # On veut équiper une arme à deux mains
            if left_item is right_item and left_item is not None and left_item.two_handed: # Les deux mains sont occupées par la même arme à deux mains
                self.add_item(left_item) # On remet l'arme dans l'inventaire (qu'une seule fois)
                self.equipped_items["left_hand"] = None # On libère les deux mains
                self.equipped_items["right_hand"] = None
            elif left_item is not None and right_item is not None and left_item is not right_item: # Les deux mains sont occupées par des armes différentes
                self.add_item(left_item) # On remet les armes dans l'inventaire
                self.add_item(right_item)
                self.equipped_items["left_hand"] = None # On libère les deux mains
                self.equipped_items["right_hand"] = None
            elif left_item is not None or right_item is not None: # Si une des deux mains est occupée
                if left_item is not None:
                    self.add_item(left_item) # On remet l'arme de la main gauche dans l'inventaire
                    self.equipped_items["left_hand"] = None # On libère la main gauche
                if right_item is not None:
                    self.add_item(right_item) # On remet l'arme de la main droite dans l'inventaire
                    self.equipped_items["right_hand"] = None # On libère la main droite
            self.equipped_items["left_hand"] = item
            self.equipped_items["right_hand"] = item
        elif item.type in ["Weapon", "Shield"] and not item.two_handed: # On veut équiper une arme à une main
            if left_item is right_item and left_item is not None: # Les deux mains sont occupées par la même arme à deux mains
                self.add_item(left_item) # On remet l'arme dans l'inventaire (qu'une seule fois)
                self.equipped_items["left_hand"] = None # On libère les deux mains
                self.equipped_items["right_hand"] = None
            if left_item is not None and right_item is not None and left_item is not right_item: # Les deux mains sont occupées par des armes différentes
                if slot == "left_hand":
                    self.add_item(left_item) # On remet l'arme de la main gauche dans l'inventaire
                    self.equipped_items["left_hand"] = None # On libère la main gauche
                else:
                    self.add_item(right_item) # On remet l'arme de la main droite dans l'inventaire
                    self.equipped_items["right_hand"] = None # On libère la main droite
            if left_item is None or right_item is None: # Si une des deux mains est libre ou les deux
                if slot == "left_hand" and left_item is not None:
                    self.add_item(left_item) # On remet l'arme de la main gauche dans l'inventaire
                    self.equipped_items["left_hand"] = None # On libère la main gauche
                elif slot == "right_hand" and right_item is not None:
                    self.add_item(right_item) # On remet l'arme de la main droite dans l'inventaire
                    self.equipped_items["right_hand"] = None # On libère la main droite
            self.equipped_items[slot] = item # On équipe l'arme dans la main choisie
        elif item.type == "Armor":
            current_item = self.equipped_items.get(slot)
            if current_item is not None:
                self.add_item(current_item) # On remet l'armure actuelle dans l'inventaire
            self.equipped_items[slot] = item


    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def list_items(self):
        return [item.name for item in self.items if item is not None] or False
    
    def get_equipped_item(self, slot):
        return self.equipped_items.get(slot, None)

    def get_equipped_weapons(self):
        return [item for item in self.equipped_items.values() if item and item.type == "Weapon"]
    
    def list_equipped_items(self):
        return {slot: item.name if item else "Empty" for slot, item in self.equipped_items.items()}