import pytest

from core.enums import Screens, Stat
from core.game.actions import AllocatePoints, ConfirmCreation, NewGame, SetName
from core.game.game import Game
from core.game.rules import CREATION_POINTS, STAT_RULES

ANY_STAT = next(iter(STAT_RULES))


@pytest.fixture
def game_in_creation() -> Game:
    game = Game()
    game.start()
    game.handle_action(NewGame())
    return game


def spend_all_points(game: Game, stat: Stat = ANY_STAT) -> None:
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


def test_confirm_leaves_creation(game_in_creation):
    game_in_creation.handle_action(SetName("Bob"))
    game_in_creation.handle_action(ConfirmCreation())
    assert game_in_creation.creation is None
    assert game_in_creation.screen is not Screens.CREATION


# --- Recommencer ------------------------------------------------------------

def test_second_new_game_starts_fresh():
    game = Game()
    game.start()
    game.handle_action(NewGame())
    game.handle_action(SetName("Bob"))
    game.handle_action(AllocatePoints(ANY_STAT, +1))

    game.handle_action(ConfirmCreation())   # retour au menu
    game.handle_action(NewGame())           # nouvelle création
    assert game.creation.name == ""
    assert game.creation.points_left == CREATION_POINTS