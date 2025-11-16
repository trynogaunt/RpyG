import questionary

def splash() -> list[str]:
    STONE = "\033[37m"
    GOLD = "\033[33m"
    RESET = "\033[0m"
    LIGHT_GRAY = "\033[38;5;250m"

    R = [
        "██████╗",
        "██╔══██╗",
        "██║  ██║",
        "██████╔╝",
        "██╔══██╗",
        "██║  ██║",
        "╚═╝  ╚═╝",
    ]

    P = [
        "██████╗",
        "██╔══██╗",
        "██████╔╝",
        "██╔═══╝ ",
        "██║     ",
        "██║     ",
        "╚═╝     ",
    ]

    Y = [
        "██╗   ██╗",
        "╚██╗ ██╔╝",
        " ╚████╔╝ ",
        "  ╚██╔╝  ",
        "   ██║   ",
        "   ██║   ",
        "   ╚═╝   ",
    ]

    G = [
        " ██████╗",
        "██╔════╝",
        "██║  ███╗",
        "██║   ██║",
        "██║   ██║",
        "╚██████╔╝",
        " ╚═════╝ ",
    ]

    slogan = f"{LIGHT_GRAY}Your CPU will handle all the dragons.{RESET}"

    # largeurs fixes par lettre
    wR = max(len(line) for line in R)
    wP = max(len(line) for line in P)
    wY = max(len(line) for line in Y)
    wG = max(len(line) for line in G)

    lines: list[str] = []
    for i in range(len(R)):
        line = (
            f"{STONE}{R[i].ljust(wR)}{RESET}   "
            f"{GOLD}{P[i].ljust(wP)}{RESET}   "
            f"{GOLD}{Y[i].ljust(wY)}{RESET}   "
            f"{STONE}{G[i].ljust(wG)}{RESET}"
        )
        lines.append(line)

    lines.append("")      # petite ligne vide
    lines.append(slogan)
    return lines

def main_menu_choice() -> str:
    choice = questionary.select(
        "Main Menu - Choose an option:",
        choices=[
            "Start New Game",
            "Load Game",
            "Settings",
            "Exit"
        ]
    ).ask()
    return choice