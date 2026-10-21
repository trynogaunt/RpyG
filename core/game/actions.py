from dataclasses import dataclass
from core.enums import Stat, Direction
from core.items.base import Slot

@dataclass(frozen=True)
class Action:
    """Player intention in the game, represented as an action that can be executed."""

@dataclass(frozen=True)
class Quit(Action):
    """Action representing the intention to quit the game."""

@dataclass(frozen=True)
class NewGame(Action):
    """Action representing the intention to start a new game."""

@dataclass(frozen=True)
class Creation(Action):
    """Action representing the intention to enter the creation screen."""

@dataclass(frozen=True)
class Options(Action):
    """Action representing the intention to open the options screen."""

@dataclass(frozen=True)
class SetLocale(Action):
    """Action representing the intention to change the game's locale."""
    locale: str

@dataclass(frozen=True)
class SetName(Action):
    """Action representing the intention to set the player's name."""
    name: str

@dataclass(frozen=True)
class AllocatePoints(Action):
    """Action representing the intention to allocate points to the player's attributes."""
    stat: Stat
    delta: int = 1


@dataclass(frozen=True)
class ChooseStarter(Action):
    """Action representing the intention to pick the starting weapon during character creation."""
    item_id: str


@dataclass(frozen=True)
class ConfirmCreation(Action):
    """Action representing the intention to confirm the creation of the player's character."""

@dataclass(frozen=True)
class Move(Action):
    """Action representing the intention to move the player in a given direction."""
    direction: Direction

@dataclass(frozen=True)
class Explore(Action):
    """Action representing the intention to explore the current room."""

@dataclass(frozen=True)
class SaveGame(Action):
    """Action representing the intention to save the current game state."""
    slot: int

@dataclass(frozen=True)
class LoadGame(Action):
    """Action representing the intention to load a previously saved game state."""
    slot: int

@dataclass(frozen=True)
class SelectSlot(Action):
    """Action representing the intention to open the details of a save slot."""
    slot: int

@dataclass(frozen=True)
class DeleteSave(Action):
    """Action representing the intention to delete a save (asks for confirmation first)."""
    slot: int

@dataclass(frozen=True)
class ConfirmDelete(Action):
    """Action representing the confirmation of a pending save deletion."""

@dataclass(frozen=True)
class Back(Action):
    """Action representing the intention to go back to the previous screen."""

@dataclass(frozen=True)
class OpenSlots(Action):
    """Action representing the intention to open the slot selection screen."""
    mode: str

@dataclass(frozen=True)
class OpenInventory(Action):
    """Action representing the intention to open the player's inventory."""

@dataclass(frozen=True)
class UseItem(Action):
    """Action representing the intention to use an item from the player's inventory."""
    index: int

@dataclass(frozen=True)
class CheckUpdate(Action):
    """Action representing the intention to check for game updates."""
    status: str

@dataclass(frozen=True)
class ApplyUpdate(Action):
    """Action representing the intention to apply a game update."""

@dataclass(frozen=True)
class InspectItem(Action):
    """Action representing the intention to look at the item stored in a bag case."""
    index: int

@dataclass(frozen=True)
class InspectEquipped(Action):
    """Action representing the intention to look at the item worn on a slot."""
    slot: Slot

@dataclass(frozen=True)
class CloseInventory(Action):
    """Action representing the intention to leave the inventory at once, whatever is selected."""

@dataclass(frozen=True)
class EquipItem(Action):
    """Action representing the intention to equip the item stored in a bag case.

    `slots` picks one of the item's slot combinations; None lets the inventory choose the first free one.
    """
    index: int
    slots: tuple[Slot, ...] | None = None

@dataclass(frozen=True)
class UnequipItem(Action):
    """Action representing the intention to put an equipped item back in the bag."""
    slot: Slot

@dataclass(frozen=True)
class OpenCatalog(Action):
    """Action representing the intention to open the item catalog."""

@dataclass(frozen=True)
class CloseCatalog(Action):
    """Action representing the intention to close the item catalog."""

@dataclass(frozen=True)
class InspectCatalogItem(Action):
    """Action representing the intention to look at an item in the catalog."""
    item_id: str

@dataclass(frozen=True)
class GiveCatalogItem(Action):
    """Action representing the intention to give an item from the catalog to the player."""
    item_id: str

@dataclass(frozen=True)
class StartCombat(Action):
    """Action representing the intention to fight an encounter of the current room."""
    encounter_id: str

@dataclass(frozen=True)
class AttackEnemy(Action):
    """Action representing the intention to strike the enemy during a combat."""
    target_index: int = 0

@dataclass(frozen=True)
class Flee(Action):
    """Action representing the intention to run away from a combat."""
