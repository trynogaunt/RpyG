from typing import List
from ui import toolkit


def render(ui, response) -> list[str]:
    lines : List[str] = []
    room = response.payload.get("room")
    message = response.message
    if not room:
        lines.extend(toolkit.header("You are nowhere. The game seems to be broken.", ui.width, ui.border_char, ui.header_char))
        return lines
    lines.extend(toolkit.header(room.name, ui.width, ui.border_char, ui.header_char))
    lines.extend(toolkit.sub_header(room.description, ui.width))
    lines.extend(toolkit.empty_line(count=1, width=ui.width, border_char=ui.border_char))
    if message:
        lines.extend(toolkit.text_block(message, ui.width, indent=ui.padding, border_char=ui.border_char))
        lines.extend(toolkit.empty_line(count=1, width=ui.width, border_char=ui.border_char))
    lines.extend(toolkit.text_block("Exits: " + ", ".join(room.exits.keys()), ui.width, indent=ui.padding, border_char=ui.border_char))
    lines.extend(toolkit.bottom_bar(ui.width, ui.header_char))
    return lines