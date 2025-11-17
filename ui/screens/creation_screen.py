def creation_header(ui: "UIController") -> list[str]:
    title = "Character Creation"
    return ui.header(title)

def resume_creation_section(state: "CharacterCreationState") -> list[str]:
    lines = []
    lines.append("Character Summary:")
    lines.append("")
    for attr, value in vars(state).items():
        lines.append(f"{attr.capitalize()}: {value}")
    return lines

def build_choices_section(choices: list[str]) -> list[str]:
    choice = questionary.select(
        "Choose your character class:",
        choices=choices
    ).ask()
    return choice

def build_name_section() -> list[str]:
    name = questionary.text("").ask()
    return name

def build_stats_section(state: "CharacterCreationState") -> list[str]:
    choice =questionary.select(message="", choices=[
        f"Health ({state.health})",
        f"Strength ({state.strength})",
        f"Speed ({state.speed})",
        f"Luck ({state.luck})",
        "Finish Allocation"
    ]).ask()
    return choice

def stop_creation_section(state: "CharacterCreationState") -> str:
    if state.points_to_spend != 0:
        choice = questionary.select(
            "You still have points to allocate. Are you sure you want to finish?",
            choices=["Yes, finish creation", "No, continue allocating points"]
        ).ask()
        return choice
def build_creation_menu(ui: "UIController", state: "CharacterCreationState") -> list[str]:
    lines = []
    lines += creation_header(ui)
    lines.append("")
    lines += resume_creation_section(state)
    if state.name == "":
        lines.append("")
        lines.append("Please enter your character's name.")
    if state.points_to_spend > 0 and state.name != "":
        lines.append("")
        lines.append(f"You have {state.points_to_spend} points to spend on attributes.")
        lines.append("Allocate points to Health, Strength, Speed, or Luck.")
    if state.points_to_spend == 0 and state.name != "":
        lines.append("")
        lines.append("You have allocated all your points. You can finish character creation.")
    
    return lines