import questionary

def main_menu():
    menu_items = [
        "Start New Game",
        "Exit"
    ]

    lines = [
        "RPyG Engine Demo",
        "Prototype build 0.1.0 – Single fight demo",    
    ]

    max_line_length = max(len(line) for line in lines)
    border = "=" * (max_line_length + 4)

    print(border)
    for line in lines:
        print(f"| {line.ljust(max_line_length)} |")
    print(border)

    choice = questionary.select(
        "Main Menu - Choose an option:",
        choices=menu_items,
    ).ask()
    if choice == "Start New Game":
        return "new_game"
    elif choice == "Exit":
        return "exit"