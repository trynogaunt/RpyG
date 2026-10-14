from dataclasses import replace

import pytest

from core.enums import Screens
from core.errors import InvalidSave
from core.game.actions import Back, CloseInventory, ConfirmCreation, EquipItem, InspectEquipped, InspectItem, NewGame, OpenInventory, SetName, UnequipItem
from core.game.game import Game
from core.game.snapshot import BagEntry, EquippedEntry
from core.items.base import Attack, Item, ItemInstance, Slot
from core.items.catalog import ItemCatalog
from core.save import codec


@pytest.fixture
def catalog() -> ItemCatalog:
    return ItemCatalog({
        "potion": Item(id="potion", max_stack=10),
        "sword": Item(id="sword", category="weapons", attack=Attack(damage_multiplier=1.5),
                      slots=((Slot.RIGHT_HAND,), (Slot.LEFT_HAND,))),
    })


@pytest.fixture
def make_game(small_world, catalog):
    def _make() -> Game:
        g = Game(world=small_world, catalog=catalog)
        g.start()
        return g
    return _make


@pytest.fixture
def game(make_game, catalog) -> Game:
    """Un personnage avec une épée usée et des potions, sur l'écran d'inventaire."""
    g = make_game()
    g.handle_action(NewGame())
    g.handle_action(SetName("Bob"))
    g.handle_action(ConfirmCreation())
    inv = g.player.inventory
    inv.add(catalog.get("sword"), instance=ItemInstance("sword", wear=0.5))
    inv.add(catalog.get("potion"), 3)
    g.handle_action(OpenInventory())
    return g


# ---------- écran d'inventaire ----------

def test_inventory_view_resolves_definitions(game):
    game.handle_action(Back())
    view = game.handle_action(OpenInventory()).view
    assert view.cases[0].item_id == "sword"
    assert view.cases[0].wear == 0.5
    assert view.cases[0].equippable
    assert not view.cases[1].equippable


def test_equip_then_unequip(game):
    view = game.handle_action(EquipItem(index=0)).view
    assert view.cases[0].item_id is None
    assert {e.slot: e.item_id for e in view.equipment if e.item_id} == {Slot.RIGHT_HAND: "sword"}

    view = game.handle_action(UnequipItem(slot=Slot.RIGHT_HAND)).view
    assert view.cases[0].item_id == "sword"
    assert all(e.item_id is None for e in view.equipment)


def test_equip_non_equippable_gives_message(game):
    response = game.handle_action(EquipItem(index=1))
    assert [m.key for m in response.messages] == ["ui.inventory.messages.cannot_equip"]


def test_back_returns_to_exploration(game):
    assert game.handle_action(Back()).screen is Screens.EXPLORATION


def worn(view) -> dict:
    return {e.slot: e.item_id for e in view.equipment if e.item_id}


def test_equip_on_chosen_slot(game):
    view = game.handle_action(EquipItem(0, slots=(Slot.LEFT_HAND,))).view
    assert worn(view) == {Slot.LEFT_HAND: "sword"}


def test_equip_without_slots_takes_first_free_combo(game):
    assert worn(game.handle_action(EquipItem(0)).view) == {Slot.RIGHT_HAND: "sword"}


def test_equip_on_forbidden_slot_gives_message(game):
    response = game.handle_action(EquipItem(0, slots=(Slot.HEAD,)))
    assert [m.key for m in response.messages] == ["ui.inventory.messages.cannot_equip"]
    assert worn(response.view) == {}


# ---------- fiche d'objet ----------

def test_inventory_opens_on_overview(game):
    assert game.handle_action(Back()).screen is Screens.EXPLORATION
    assert game.handle_action(OpenInventory()).view.selected is None


def test_inspect_bag_item_shows_its_definition(game):
    d = game.handle_action(InspectItem(0)).view.selected
    assert d.item_id == "sword"
    assert d.category == "weapons"
    assert d.attack.damage_multiplier == 1.5
    assert d.wear == 0.5
    assert d.index == 0 and d.equipped_on is None
    assert d.can_equip and not d.can_unequip


def test_inspect_stack_shows_quantity(game):
    d = game.handle_action(InspectItem(1)).view.selected
    assert d.quantity == 3
    assert not d.can_equip


@pytest.mark.parametrize("index", [5, -1, 999])
def test_inspect_empty_or_invalid_case_is_ignored(game, index):
    assert game.handle_action(InspectItem(index)).view.selected is None


def test_inspect_equipped_item(game):
    game.handle_action(EquipItem(0))
    d = game.handle_action(InspectEquipped(Slot.RIGHT_HAND)).view.selected
    assert d.item_id == "sword"
    assert d.equipped_on == (Slot.RIGHT_HAND,)
    assert d.can_unequip and not d.can_equip


def test_inspect_empty_slot_is_ignored(game):
    assert game.handle_action(InspectEquipped(Slot.HEAD)).view.selected is None


def test_equip_from_detail_returns_to_overview(game):
    game.handle_action(InspectItem(0))
    view = game.handle_action(EquipItem(0)).view
    assert view.selected is None
    assert view.equipment[0].item_id == "sword"


def test_back_closes_detail_before_leaving(game):
    game.handle_action(InspectItem(0))
    response = game.handle_action(Back())
    assert response.screen is Screens.INVENTORY and response.view.selected is None
    assert game.handle_action(Back()).screen is Screens.EXPLORATION


def test_inspecting_an_empty_slot_clears_the_selection(game):
    game.handle_action(InspectItem(0))
    assert game.handle_action(InspectEquipped(Slot.HEAD)).view.selected is None
    game.handle_action(InspectItem(0))
    assert game.handle_action(InspectItem(7)).view.selected is None


def test_close_inventory_leaves_at_once(game):
    game.handle_action(InspectItem(0))
    response = game.handle_action(CloseInventory())
    assert response.screen is Screens.EXPLORATION
    assert game.inventory_selection is None


def test_reopening_inventory_resets_selection(game):
    game.handle_action(InspectItem(0))
    game.inventory_selection = 0          # sélection laissée ouverte...
    game.screen = Screens.EXPLORATION     # ...puis sortie par un autre chemin
    assert game.handle_action(OpenInventory()).view.selected is None


# ---------- sauvegarde ----------

def test_snapshot_restore_roundtrip_with_inventory(game, make_game):
    game.handle_action(EquipItem(index=0))
    snap = game.snapshot()
    assert snap.player.equipped == (EquippedEntry((Slot.RIGHT_HAND,), ItemInstance("sword", wear=0.5)),)
    assert snap.player.bag == (BagEntry(1, ItemInstance("potion"), 3),)

    other = make_game()
    other.restore(snap)
    assert other.snapshot() == snap


def test_codec_roundtrip_with_inventory(game):
    game.handle_action(EquipItem(index=0))
    snap = game.snapshot()
    assert codec.decode(codec.encode(snap)) == snap


def test_decode_v1_0_save_has_empty_inventory(game):
    data = codec.encode(game.snapshot())
    data["version"] = "1.0"
    del data["player"]["inventory"]
    snap = codec.decode(data)
    assert snap.player.bag == () and snap.player.equipped == ()


def test_decode_unknown_slot_raises(game):
    game.handle_action(EquipItem(index=0))
    data = codec.encode(game.snapshot())
    data["player"]["inventory"]["equipped"][0]["slots"] = ["tail"]
    with pytest.raises(InvalidSave):
        codec.decode(data)


def _with_player(snap, **changes):
    return replace(snap, player=replace(snap.player, **changes))


@pytest.mark.parametrize("bag", [
    (BagEntry(0, ItemInstance("ghost"), 1),),                                    # item inconnu
    (BagEntry(99, ItemInstance("potion"), 1),),                                  # case hors du sac
    (BagEntry(0, ItemInstance("potion"), 1), BagEntry(0, ItemInstance("potion"), 1)),  # même case
    (BagEntry(0, ItemInstance("potion"), 11),),                                  # dépasse max_stack
])
def test_restore_invalid_bag_raises(game, bag):
    before = game.snapshot()
    with pytest.raises(InvalidSave):
        game.restore(_with_player(before, bag=bag))
    assert game.snapshot() == before


@pytest.mark.parametrize("equipped", [
    (EquippedEntry((Slot.HEAD,), ItemInstance("sword")),),                       # slot interdit
    (EquippedEntry((Slot.RIGHT_HAND,), ItemInstance("potion")),),                # pas équipable
    (EquippedEntry((Slot.RIGHT_HAND,), ItemInstance("sword")),
     EquippedEntry((Slot.RIGHT_HAND,), ItemInstance("sword"))),                  # slot déjà pris
])
def test_restore_invalid_equipment_raises(game, equipped):
    with pytest.raises(InvalidSave):
        game.restore(_with_player(game.snapshot(), equipped=equipped))
