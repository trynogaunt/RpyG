from typing import Iterable, List
from ui import toolkit


def build_room_screen(ui, response) -> list[str]:
    lines : List[str] = []
    room = response.payload.get("room") # room is of type RoomInstance
    message = response.message
    if room:
        lines.extend(toolkit.room_header(ui, room.get_label, room.get_description))
    else:
        lines.append("You are nowhere. The game seems to be broken.")
    if message:
        lines.append(message)
    return lines