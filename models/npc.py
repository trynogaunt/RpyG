class NPC():
    def __init__(self, name, role, dialogue=None):
        self.name = name
        self.role = role
        self.dialogue = dialogue if dialogue is not None else []

    def speak(self):
        if self.dialogue:
            return self.dialogue[0]  # Simple implementation: always return the first line
        return "..."

class ShopKeeper(NPC):
    def __init__(self, name, shop : list['Item']=None, dialogue=None):
        super().__init__(name, role="ShopKeeper", dialogue=dialogue)
        self.shop = shop if shop is not None else []

    def list_items_for_sale(self):
        shop_list = []
        for item in self.shop:
            shop_list.append(f"- {item.name}: {item.price} gold")
        return shop_list