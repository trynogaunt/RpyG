def load_npc_data():
    import json
    from models.npc import NPC

    with open('world/entities/npc.json', 'r') as file:
        npc_data = json.load(file)

    npcs = {}
    for npc_class in npc_data:
        npc_info = npc_data[npc_class]
        npc = NPC(
            name=npc_info['name'],
            dialogue=npc_info['dialogue'],
            role=npc_info['role']
        )
        npcs["Gorim the Blacksmith"] = npc

    assert "Gorim the Blacksmith" in npcs


def load_shopkeeper_data():
    import json
    from models.npc import ShopKeeper, ROLE_CLASSES
    from models.item import Item

    with open('world/entities/npc.json', 'r') as file:
        shopkeeper_data = json.load(file)

    shopkeepers = {}
    for shopkeeper_class in shopkeeper_data:
        shopkeeper_info = shopkeeper_data[shopkeeper_class]
        items_for_sale = [Item(name=item['name'], description=item['description']) for item in shopkeeper_info['shop']]
        shopkeeper = ShopKeeper(
            name=shopkeeper_info['name'],
            shop=items_for_sale,
            dialogue=shopkeeper_info['dialogue']
        )
        shopkeepers[shopkeeper_info['name']] = shopkeeper

    assert "Gorim the Blacksmith" in shopkeepers

if __name__ == "__main__":
    load_npc_data()
    print("NPC data loaded successfully.")