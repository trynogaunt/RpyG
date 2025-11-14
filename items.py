from classes import item

COMMON_WEAPON = [
    item.Weapon("Rusty Sword", "An old and rusty sword.", 5, allowed_parts=["right_hand", "left_hand"], damage_type="Physical", ignore_defense=False),
    item.Weapon("Wooden Bow", "A simple wooden bow.", 4, allowed_parts=["right_hand", "left_hand"], damage_type="Physical", ignore_defense=False),
    item.Weapon("Stone Dagger", "A dagger made of stone.", 3, allowed_parts=["right_hand", "left_hand"], damage_type="Physical", ignore_defense=False)

]

COMMON_ARMOR = [
    item.Armor("Leather Helmet", "A basic leather helmet.", 2, part="head", allowed_parts=["head"]),
    item.Armor("Cloth Tunic", "A simple cloth tunic.", 1, part="torso", allowed_parts=["torso"]),
    item.Armor("Leather Boots", "Worn leather boots.", 1, part="feet", allowed_parts=["feet"]),
    item.Armor("Cloth Pants", "Basic cloth pants.", 1, part="legs", allowed_parts=["legs"])   
]