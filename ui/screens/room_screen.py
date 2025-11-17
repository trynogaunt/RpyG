from typing import Iterable, List
from ui import toolkit


def build_room_screen(ui, room, message: str = "") -> list[str]:
    lines : List[str] = []
    if room:
        lines.extend(toolkit.room_header(ui, room.name, room.description))
    else:
        lines.append("You are nowhere. The game seems to be broken.")
    if message:
        lines.append(message)
    return lines