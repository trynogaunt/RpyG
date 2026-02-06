from typing import Iterable, List
from ui import toolkit

def render(ui, response):
    lines = []
    golds = response.payload.get("golds", 0)
    items : List[str] = response.payload.get("items", [])
    equipped = response.payload.get("equipped", {})
    width = ui.width
    b_char = ui.border_char
    padding = ui.padding
    header_char = ui.header_char
    
    lines.extend(toolkit.header("Inventory", width, border_char=b_char, h_char=header_char))
    lines.extend(toolkit.left_text(f"Golds {golds}", width, border_char=b_char))
    lines.extend(toolkit.empty_line(1,width, border_char=b_char))
    items_col : List[str] = [item for item in items] if items else ["No items in inventory"]
    
    slot_col : List[str] = []
    for slot, item in equipped.items():
        if item:
            slot_col.append(f"{slot.replace('_', ' ').title()}: {item}")
        else:
            slot_col.append(f"{slot.replace('_', ' ').title()}: Empty")
    
    lines.extend(toolkit.two_column(["Backpack", ""] + items_col, ["Equipped Items", ""] + slot_col, width, border_char=b_char, indent=1))
    lines.extend(toolkit.bottom_bar(width, h_char=header_char))
    return lines