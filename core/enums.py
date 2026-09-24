from enum import Enum, auto

class Screens(Enum):
    MAIN_MENU = auto()
    INVENTORY = auto()
    CREATION = auto()
    PAUSE_MENU = auto()
    GAME_OVER = auto()
    EXIT = auto()

class Stat(Enum):
    HEALTH = auto()
    STRENGTH = auto()
    SPEED = auto()
    LUCK = auto()