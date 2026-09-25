import pytest

from core.enums import Direction, Screens
from core.game.actions import Action, ConfirmCreation, Move, NewGame, Quit, SetName
from core.world.models import RoomRef


@pytest.fixture
def game_exploring(game_in_creation):
    """Un jeu où le personnage vient d'être créé : il est dans la salle de départ."""
    game_in_creation.handle_action(SetName("Bob"))
    game_in_creation.handle_action(ConfirmCreation())
    return game_in_creation


# --- Arrivée dans le monde --------------------------------------------------------

def test_starts_on_exploration_screen(game_exploring):
    assert game_exploring.screen is Screens.EXPLORATION


def test_player_starts_at_world_start(game_exploring):
    assert game_exploring.player.location == RoomRef("village", "square")


# --- Quitter ------------------------------------------------------------------------

def test_quit_returns_to_main_menu(game_exploring):
    response = game_exploring.handle_action(Quit())
    assert response.screen is Screens.MAIN_MENU


def test_new_game_during_exploration_raises(game_exploring):
    # NewGame n'a de sens que depuis le menu : ici c'est un bug de l'UI
    with pytest.raises(ValueError):
        game_exploring.handle_action(NewGame())


def test_unknown_action_raises(game_exploring):
    class UnknownAction(Action):
        pass

    with pytest.raises(ValueError):
        game_exploring.handle_action(UnknownAction())


# --- Déplacements (à faire passer avec l'action Move) ---------------------------

def test_move_to_existing_exit(game_exploring):
    game_exploring.handle_action(Move(Direction.SOUTH))
    assert game_exploring.player.location == RoomRef("village", "gate")


def test_move_stays_on_exploration_screen(game_exploring):
    response = game_exploring.handle_action(Move(Direction.SOUTH))
    assert response.screen is Screens.EXPLORATION


def test_move_without_exit_is_ignored(game_exploring):
    # La place n'a pas de sortie au nord
    game_exploring.handle_action(Move(Direction.NORTH))
    assert game_exploring.player.location == RoomRef("village", "square")


def test_move_and_come_back(game_exploring):
    game_exploring.handle_action(Move(Direction.SOUTH))
    game_exploring.handle_action(Move(Direction.NORTH))
    assert game_exploring.player.location == RoomRef("village", "square")


def test_move_to_another_zone(game_exploring):
    game_exploring.handle_action(Move(Direction.SOUTH))   # place -> porte
    game_exploring.handle_action(Move(Direction.SOUTH))   # porte -> grotte
    assert game_exploring.player.location == RoomRef("cave", "entrance")


def test_move_back_from_another_zone(game_exploring):
    for direction in (Direction.SOUTH, Direction.SOUTH, Direction.NORTH):
        game_exploring.handle_action(Move(direction))
    assert game_exploring.player.location == RoomRef("village", "gate")


def test_player_always_in_an_existing_room(game_exploring):
    path = [Direction.SOUTH, Direction.SOUTH, Direction.SOUTH, Direction.EAST,
            Direction.NORTH, Direction.NORTH, Direction.WEST, Direction.NORTH]
    for direction in path:
        game_exploring.handle_action(Move(direction))
        game_exploring.world.get_room(game_exploring.player.location)   # ne doit pas lever