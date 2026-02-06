from ui import toolkit as tk
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ui.ui_controller import UIController
    from events.response import GameResponse


def render(ui: "UIController", response : "GameResponse") -> List[str]:
    step = response.payload.get("step")
    width = ui.width
    b_char = ui.border_char
    padding = ui.padding
    header_char = ui.header_char
    step = response.payload.get("step", 1)
    character_name = response.payload.get("character_name", "Adventurer") if step <= 1 and isinstance(response.payload.get("character_name"), str) else None
    available_points = response.payload.get("available_points", 10) if step == 2 and isinstance(response.payload.get("available_points"), int) else 10
    character_stats = response.payload.get("character_stats", {"Health": 10, "Strength": 5, "Speed": 5, "Luck": 1}) if step == 2 and isinstance(response.payload.get("character_stats"), dict) else {"Health": 10, "Strength": 5, "Speed": 5, "Luck": 1}
    lines = []
    
    lines.extend(tk.header("Character Creation", width, b_char, header_char))
    lines.extend(tk.empty_line(count=1, width=width, border_char=b_char))
    lines.extend(tk.text_block("Welcome to the character creation screen! Here you can customize your adventurer before embarking on your journey. Follow the steps to create a unique character that suits your playstyle.", width, indent=padding, border_char=b_char))
    lines.extend(tk.empty_line(count=1, width=width, border_char=b_char))
    lines.extend(tk.empty_line(count=1, width=width, border_char=b_char))
    lines.extend(tk.text_block(f"Character Name: {character_name}", width, indent=padding, border_char=b_char))
    if step == 2 or character_name is not None:
        lines.extend(tk.empty_line(count=1, width=width, border_char=b_char))
        lines.extend(tk.text_block(f"Available Points: {available_points}", width, indent=padding, border_char=b_char))
        lines.extend(tk.empty_line(count=1, width=width, border_char=b_char))
        lines.extend(tk.text_block("Character Stats:", width, indent=padding, border_char=b_char))
        for stat, value in character_stats.items():
            lines.extend(tk.text_block(f"{stat}: {value}", width, indent=padding*2, border_char=b_char))
    lines.extend(tk.empty_line(count=1, width=width, border_char=b_char))
    lines.extend(tk.right_text(f"{step}/3", width,border_char=b_char))
    lines.extend(tk.bottom_bar(width, header_char))
    return lines
