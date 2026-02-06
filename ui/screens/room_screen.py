from ui import toolkit as tk
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ui.ui_controller import UIController
    from events.response import GameResponse


def render(ui: "UIController", response: "GameResponse") -> List[str]:
    lines : List[str] = []
    room = response.payload.get("room")
    message = response.message
    if not room:
        lines.extend(tk.header("You are nowhere. The game seems to be broken.", ui.width, ui.border_char, ui.header_char))
        return lines
    lines.extend(tk.header(room.name, ui.width, ui.border_char, ui.header_char))
    lines.extend(tk.sub_header(room.description, ui.width, border_char=ui.border_char))
    lines.extend(tk.empty_line(count=1, width=ui.width, border_char=ui.border_char))
    if message:
        lines.extend(tk.text_block(message, ui.width, indent=ui.padding, border_char=ui.border_char))
        lines.extend(tk.empty_line(count=1, width=ui.width, border_char=ui.border_char))
    lines.extend(tk.text_block("Exits: " + ", ".join(room.exits.keys()), ui.width, indent=ui.padding, border_char=ui.border_char))
    lines.extend(tk.bottom_bar(ui.width, ui.header_char))
    return lines