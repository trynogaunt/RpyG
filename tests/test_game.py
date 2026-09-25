import pytest

from core.enums import Screens
from core.game.actions import Action, NewGame, Quit
from core.game.game import Game


def test_start_returns_main_menu(small_world):
    response = Game(world=small_world).start()
    assert response.screen is Screens.MAIN_MENU


def test_game_keeps_the_world(small_world):
    assert Game(world=small_world).world is small_world


def test_new_game_from_menu_goes_to_creation(game):
    response = game.handle_action(NewGame())
    assert response.screen is Screens.CREATION


def test_quit_from_menu_goes_to_exit(game):
    response = game.handle_action(Quit())
    assert response.screen is Screens.EXIT


def test_new_game_outside_menu_is_ignored(game):
    game.handle_action(NewGame())             # menu -> création
    response = game.handle_action(NewGame())  # hors contexte
    assert response.screen is Screens.CREATION


def test_unknown_action_raises(game):
    class UnknownAction(Action):
        pass

    with pytest.raises(ValueError):
        game.handle_action(UnknownAction())