from ui import toolkit as tk
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ui.ui_controller import UIController
    from events.response import GameResponse

def render(ui: "UIController", response: "GameResponse")-> List[str]:
    width = ui.width
    b_char = ui.border_char
    padding = ui.padding
    header_char = ui.header_char
    lines = []
    lines.extend(tk.header("R P y G  -  L E G A C Y", width, b_char, header_char))
    lines.extend(tk.empty_line(count=2))
    lines.extend(tk.splash(width, b_char))
    intro_text = "In a world where dragons roam the skies and ancient magic lingers in the air, you are a brave adventurer seeking fame and fortune. Will you conquer the challenges that await and become a legend?"
    version_info = tk.color_text("Version 0.1 - Early Access", tk.Colors.LIGHT_GRAY.value)
    lines.extend(tk.bottom_bar(width, header_char))
    lines.extend(tk.text_block(intro_text, width, indent=padding, border_char=b_char))
    lines.extend(tk.empty_line(count=2, width=width, border_char=b_char))
    lines.extend(tk.center_text(version_info, width, b_char))
    lines.extend(tk.bottom_bar(width, header_char))
    lines.extend(tk.empty_line(count=2))
    return lines