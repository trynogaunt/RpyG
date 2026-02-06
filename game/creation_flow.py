from ui.screens.creation_screen import build_creation_menu, build_name_section, build_stats_section, stop_creation_section
from classes.interface_class import CharacterCreationState
from models.hero import Hero
from enums import  CreationMenuOption, AttributeType, YesNoOption
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.ui_controller import UIController

def create_character(ui: "UIController") -> Hero:
    state = CharacterCreationState()
    while state.name == "":
        creation_menu_lines = build_creation_menu(ui, state)
        ui.render(creation_menu_lines)
        name = build_name_section()
        state.name = name

    while state.points_to_spend > 0:
        creation_menu_lines = build_creation_menu(ui, state)
        ui.render(creation_menu_lines)
        choice = build_stats_section(state)
        if choice.__contains__(AttributeType.HEALTH):
            state.health += 5
            state.points_to_spend -= 1
        elif choice.__contains__(AttributeType.STRENGTH):
            state.strength += 1
            state.points_to_spend -= 1
        elif choice.__contains__(AttributeType.SPEED):
            state.speed += 1
            state.points_to_spend -= 1
        elif choice.__contains__(AttributeType.LUCK):
            state.luck += 1
            state.points_to_spend -= 1
        elif choice == CreationMenuOption.FINISH:
            stop_choice = stop_creation_section(state)
            if stop_choice == YesNoOption.YES:
                state.points_to_spend = 0
                break
            else:
                continue
    hero = Hero(
        name=state.name,
        health=state.health,
        strength=state.strength,
        speed=state.speed,
        luck=state.luck,
    )
    creation_menu_lines = build_creation_menu(ui, state)
    ui.render(creation_menu_lines)
    return hero
