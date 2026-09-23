from enum import Enum, auto

class Screen(Enum):
    MAIN_MENU = auto()
    INVENTORY = auto()
    CREATION = auto()
    PAUSE_MENU = auto()
    GAME_OVER = auto()
    EXIT = auto()