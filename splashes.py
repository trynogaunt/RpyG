import os
import time

STONE = "\033[37m"
GOLD = "\033[33m"
RESET = "\033[0m"

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

slogan = f"{STONE}Your CPU will handle all the dragons.{RESET}"


def splash():
    os.system("cls" if os.name == "nt" else "clear")

    # largeurs fixes par lettre
    wR = max(len(line) for line in R)
    wP = max(len(line) for line in P)
    wY = max(len(line) for line in Y)
    wG = max(len(line) for line in G)

    for i in range(len(R)):
        line = (
            f"{STONE}{R[i].ljust(wR)}{RESET}   "
            f"{STONE}{P[i].ljust(wP)}{RESET}   "
            f"{STONE}{Y[i].ljust(wY)}{RESET}   "
            f"{GOLD}{G[i].ljust(wG)}{RESET}"
        )
        print(line)
        time.sleep(0.08)

    print()
    time.sleep(0.3)
    print(slogan)
    time.sleep(1.0)
