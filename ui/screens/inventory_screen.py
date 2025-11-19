from typing import Iterable, List
from ui import toolkit

def build_inventory_screen(ui, response):
    items = response.payload.get("items", [])
    equipped = response.payload.get("equipped", [])
    gold = response.payload.get("gold", 0)
    lines = []
    lines.extend(ui.header("Inventory"))
    lines.extend(ui.sub_header("Your own portal to treasures and gear"))
    lines.append(f"Gold: {gold}")
    lines.append("Equipped Items:")
    if equipped:
        for item in equipped:
            lines.append(f" - {item}")
    else:
        lines.append(" (none)")
        lines.append("")
    lines.append("Inventory Items:")
    if items:
        for item in items:
            lines.append(f" - {item}")
    else:
        lines.append(" (empty)")
    return lines