from enum import Enum

class MainMenuOption(str, Enum):
    NEW_GAME = "Start New Game"
    LOAD_GAME = "Load Game"
    SETTINGS = "Settings"
    EXIT = "Exit"
    
class CreationMenuOption(str, Enum):
    NAME = "Name"
    STATS = "Stats"
    FINISH = "Finish"

class AttributeType(str, Enum):
    HEALTH = "Health"
    STRENGTH = "Strength"
    SPEED = "Speed"
    LUCK = "Luck"
    
class InventoryOption(str, Enum):
    USE = "Use"
    DROP = "Drop"
    INSPECT = "Inspect"
    BACK = "Back"
    
class CombatOption(str, Enum):
    ATTACK = "Attack"
    DEFEND = "Defend"
    USE_ITEM = "Use Item"
    FLEE = "Flee"

class ExplorationOption(str, Enum):
    MOVE = "Move"
    SEARCH = "Search"
    INTERACT = "Interact"
    INVENTORY = "Inventory"

class YesNoOption(str, Enum):
    YES = "Yes"
    NO = "No"
    
