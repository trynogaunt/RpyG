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
    step = response.payload.get("step")
    stats_names = response.payload.get("stats_names", {}) if isinstance(response.payload.get("stats_names"), dict) else {}
    character_name = response.payload.get("character_name", "Adventurer") if isinstance(response.payload.get("character_name"), str) else ""
    available_points = response.payload.get("available_points", 10) if isinstance(response.payload.get("available_points"), int) else 10
    character_stats = response.payload.get("character_stats", {"health": 10, "strength": 5, "speed": 5, "luck": 1}) 
        
    stats_description = response.payload.get("stats_description") if isinstance(response.payload.get("stats_description"), dict) else {}
    lines = []
    lines.extend(tk.header(ui.ctx.t("ui.creation.title"), width, b_char, header_char))
    lines.extend(tk.empty_line(count=1, width=width, border_char=b_char))
    lines.extend(tk.text_block(ui.ctx.t("ui.creation.prompt_start"), width, indent=padding, border_char=b_char))
    lines.extend(tk.empty_line(count=1, width=width, border_char=b_char))
    lines.extend(tk.empty_line(count=1, width=width, border_char=b_char))
    lines.extend(tk.text_block(ui.ctx.t("ui.creation.character_name", name=character_name), width, indent=padding, border_char=b_char))
    lines.extend(tk.empty_line(count=1, width=width, border_char=b_char))
    lines.extend(tk.text_block(ui.ctx.t("ui.creation.available_points", points=available_points), width, indent=padding, border_char=b_char))
    lines.extend(tk.empty_line(count=1, width=width, border_char=b_char))
    lines.extend(tk.text_block(ui.ctx.t("ui.creation.stats.prompt.title"), width, indent=padding, border_char=b_char))
    left_column = []
    right_column = []
    for stat, value in character_stats.items():
        if stat in stats_description:
            left_column.extend(tk.text_block(f"{stats_names.get(stat, stat.capitalize())}: {value}", width, indent=padding*2, border_char=""))
            right_column.extend(tk.text_block(f"{stats_description[stat]}", width, indent=padding*2, border_char=""))
    lines.extend(tk.two_column(left_column, right_column, width, border_char=b_char, col_width=(30, 70), separator="#", indent=2, linked=True))
    lines.extend(tk.empty_line(count=1, width=width, border_char=b_char))
    lines.extend(tk.right_text(f"{step}/3", width,border_char=b_char))
    lines.extend(tk.bottom_bar(width, header_char))
    return lines
