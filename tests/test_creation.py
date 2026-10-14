import pytest

from core.enums import Screens, Stat
from core.game.actions import AllocatePoints, ConfirmCreation, NewGame, SetName
from core.game.rules import CREATION_POINTS, STAT_RULES

ANY_STAT = next(iter(STAT_RULES))

# La fixture `game_in_creation` vient de tests/conftest.py


def spend_all_points(game, stat=ANY_STAT) -> None:
    for _ in range(CREATION_POINTS):
        game.handle_action(AllocatePoints(stat, +1))


# --- Entrée en création -----------------------------------------------------

def test_new_game_opens_creation(game_in_creation):
    assert game_in_creation.screen is Screens.CREATION
    assert game_in_creation.creation is not None


def test_creation_starts_empty(game_in_creation):
    creation = game_in_creation.creation
    assert creation.name == ""
    assert creation.points_left == CREATION_POINTS
    for stat, rule in STAT_RULES.items():
        assert creation.stat_value(stat) == rule.base


def test_no_player_before_confirmation(game_in_creation):
    assert game_in_creation.player is None


# --- Nom ---------------------------------------------------------------------

def test_set_name(game_in_creation):
    game_in_creation.handle_action(SetName("Bob"))
    assert game_in_creation.creation.name == "Bob"


def test_set_name_strips_spaces(game_in_creation):
    game_in_creation.handle_action(SetName("  Bob  "))
    assert game_in_creation.creation.name == "Bob"


@pytest.mark.parametrize("blank", ["", "   "])
def test_blank_name_prevents_confirm(game_in_creation, blank):
    game_in_creation.handle_action(SetName("Bob"))
    game_in_creation.handle_action(SetName(blank))
    assert game_in_creation.creation.name == ""
    assert not game_in_creation.creation.can_confirm()


# --- Répartition des points ------------------------------------------------

@pytest.mark.parametrize("stat", list(STAT_RULES))
def test_add_point_raises_stat_by_per_point(game_in_creation, stat):
    creation = game_in_creation.creation
    before = creation.stat_value(stat)
    game_in_creation.handle_action(AllocatePoints(stat, +1))
    assert creation.stat_value(stat) - before == STAT_RULES[stat].per_point
    assert creation.points_left == CREATION_POINTS - 1


@pytest.mark.parametrize("stat", list(STAT_RULES))
def test_cannot_go_below_base(game_in_creation, stat):
    game_in_creation.handle_action(AllocatePoints(stat, -1))
    creation = game_in_creation.creation
    assert creation.stat_value(stat) == STAT_RULES[stat].base
    assert creation.points_left == CREATION_POINTS


def test_cannot_spend_more_than_available(game_in_creation):
    spend_all_points(game_in_creation)
    creation = game_in_creation.creation
    assert creation.points_left == 0

    game_in_creation.handle_action(AllocatePoints(ANY_STAT, +1))
    assert creation.points_left == 0
    assert creation.allocated_points[ANY_STAT] == CREATION_POINTS


def test_remove_point_undoes_add(game_in_creation):
    creation = game_in_creation.creation
    before = dict(creation.allocated_points)
    game_in_creation.handle_action(AllocatePoints(ANY_STAT, +1))
    game_in_creation.handle_action(AllocatePoints(ANY_STAT, -1))
    assert creation.allocated_points == before
    assert creation.points_left == CREATION_POINTS


def test_invalid_delta_raises(game_in_creation):
    with pytest.raises(ValueError):
        game_in_creation.handle_action(AllocatePoints(ANY_STAT, 2))


# --- Confirmation -----------------------------------------------------------

def test_cannot_confirm_without_name(game_in_creation):
    game_in_creation.handle_action(ConfirmCreation())
    assert game_in_creation.player is None
    assert game_in_creation.screen is Screens.CREATION


def test_confirm_with_unspent_points(game_in_creation):
    game_in_creation.handle_action(SetName("Bob"))
    game_in_creation.handle_action(ConfirmCreation())
    assert game_in_creation.player is not None


def test_confirm_builds_player_from_creation(game_in_creation):
    game_in_creation.handle_action(SetName("Bob"))
    game_in_creation.handle_action(AllocatePoints(Stat.HEALTH, +1))
    expected_health = game_in_creation.creation.stat_value(Stat.HEALTH)

    game_in_creation.handle_action(ConfirmCreation())
    player = game_in_creation.player
    assert player.name == "Bob"
    assert player.allocated_points[Stat.HEALTH] == 1
    assert player.max_health == expected_health
    assert player.health == player.max_health


def test_confirm_goes_to_exploration(game_in_creation):
    game_in_creation.handle_action(SetName("Bob"))
    response = game_in_creation.handle_action(ConfirmCreation())
    assert response.screen is Screens.EXPLORATION
    assert game_in_creation.creation is None


def test_confirm_places_player_at_world_start(game_in_creation):
    game_in_creation.handle_action(SetName("Bob"))
    game_in_creation.handle_action(ConfirmCreation())
    assert game_in_creation.player.location == game_in_creation.world.start


# --- Recommencer ------------------------------------------------------------

def test_new_game_after_quitting_starts_fresh(game_in_creation):
    from core.game.actions import Quit

    game = game_in_creation
    game.handle_action(SetName("Bob"))
    game.handle_action(AllocatePoints(ANY_STAT, +1))
    game.handle_action(ConfirmCreation())   # -> exploration
    game.handle_action(Quit())              # -> menu
    game.handle_action(NewGame())           # -> nouvelle création
    assert game.creation.name == ""
    assert game.creation.points_left == CREATION_POINTS

# --- Arme de départ -----------------------------------------------------------

from core.game.actions import ChooseStarter
from core.game.game import Game
from core.game.rules import STARTER_WEAPONS
from core.items.base import Item, ItemInstance, Slot
from core.items.catalog import ItemCatalog

HANDS = ((Slot.RIGHT_HAND,), (Slot.LEFT_HAND,))


@pytest.fixture
def armed_creation(small_world) -> Game:
    """Création avec un catalogue contenant les deux premières armes de départ."""
    first, second = STARTER_WEAPONS[:2]
    catalog = ItemCatalog({
        first: Item(id=first, slots=HANDS),
        second: Item(id=second, slots=HANDS),
        "potion": Item(id="potion", max_stack=10),
    })
    g = Game(world=small_world, catalog=catalog)
    g.start()
    g.handle_action(NewGame())
    g.handle_action(SetName("Bob"))
    return g


def test_starter_choices_come_from_rules_filtered_by_catalog(armed_creation):
    assert armed_creation.creation.starter_choices == STARTER_WEAPONS[:2]


def test_first_starter_is_preselected(armed_creation):
    assert armed_creation.creation.starter == STARTER_WEAPONS[0]


def test_choose_starter(armed_creation):
    view = armed_creation.handle_action(ChooseStarter(STARTER_WEAPONS[1])).view
    assert view.starter == STARTER_WEAPONS[1]


def test_choose_item_outside_choices_is_ignored(armed_creation):
    armed_creation.handle_action(ChooseStarter("potion"))
    assert armed_creation.creation.starter == STARTER_WEAPONS[0]


def test_confirm_puts_a_fresh_starter_in_the_bag(armed_creation):
    armed_creation.handle_action(ChooseStarter(STARTER_WEAPONS[1]))
    armed_creation.handle_action(ConfirmCreation())
    first = armed_creation.player.inventory.cases[0]
    assert first.instance == ItemInstance(STARTER_WEAPONS[1], wear=1.0)
    assert first.quantity == 1


def test_no_catalog_means_no_starter(game_in_creation):
    game_in_creation.handle_action(SetName("Bob"))
    assert game_in_creation.creation.starter_choices == ()
    game_in_creation.handle_action(ConfirmCreation())
    assert all(c.is_empty for c in game_in_creation.player.inventory.cases)
