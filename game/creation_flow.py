from ui.screens.creation_screen import build_creation_menu, build_name_section, build_stats_section, stop_creation_section
from classes.interface_class import CharacterCreationState
from classes.hero import Hero

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
        if choice.__contains__("Health"):
            state.health += 5
            state.points_to_spend -= 1
        elif choice.__contains__("Strength"):
            state.strength += 1
            state.points_to_spend -= 1
        elif choice.__contains__("Speed"):
            state.speed += 1
            state.points_to_spend -= 1
        elif choice.__contains__("Luck"):
            state.luck += 1
            state.points_to_spend -= 1
        elif choice == "Finish Allocation":
            stop_choice = stop_creation_section(state)
            if stop_choice == "Yes, finish creation":
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
    
    return hero
