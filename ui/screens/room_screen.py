from ui.ui_controller import UIController
from typing import Iterable, List
from classes.character import Character
import questionary

def room_header(ui, room_name: str, room_description: str) -> list[str]:
    return ui.header(room_name)

def choices_section(actions: list[str]) -> str:
    choice = questionary.select(
        "What would you like to do?",
        choices=actions
    ).ask()
    return choice


def build_room_screen(ui: UIController, hero: Character, actions: list[str]) -> list[str]:
    lines = []
    if hero.current_room:
        lines.extend(room_header(ui, hero.current_room.name, hero.current_room.description))
        lines.extend(ui.sub_header(hero.current_room.description))
    else:
        lines.append("You are nowhere. The game seems to be broken.")
    return lines