ROLE_CLASSES = {
    "blacksmith": ShopKeeper,
    "citizen": NPC,
}

class NPC():
    def __init__(self, name, role, dialogue=None):
        self.id = name.lower().replace(" ", "_")
        self.name = name
        self.description = f"A {role} named {name}."
        self.role = role
        self.gold = 0
        self.dialogue = dialogue if dialogue is not None else []

    def speak(self):
        if self.dialogue:
            return self.dialogue[0]  # Simple implementation: always return the first line
        return "..."

class ShopKeeper(NPC):
    def __init__(self, name, shop : list['Item']=None, dialogue=None):
        super().__init__(name, role="ShopKeeper", dialogue=dialogue)
        self.shop = shop if shop is not None else []

    def greet(self):
        return any(dialogue for dialogue in self.dialogue if "welcome" or "greetings" in dialogue.lower()) or f"Welcome to my shop"
    
    def add_item_for_sale(self, item):
        self.shop.append(item)
    
    def remove_item_for_sale(self, item):
        if item in self.shop:
            self.shop.remove(item)
            
    def list_items_for_sale(self):
        shop_list = []
        for item in self.shop:
            shop_list.append(f"- {item.name}: {item.price} gold")
        return shop_list