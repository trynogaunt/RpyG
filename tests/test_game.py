import pytest

from core.enums import Screen
from core.game.actions import Action, NewGame, Quit
from core.game.game import Game


@pytest.fixture
def game_in_menu() -> Game:
    game = Game()
    game.start()
    return game


def test_start_returns_main_menu():
    response = Game().start()
    assert response.screen is Screen.MAIN_MENU


def test_new_game_from_menu_goes_to_creation(game_in_menu):
    response = game_in_menu.handle_action(NewGame())
    assert response.screen is Screen.CREATION


def test_quit_from_menu_goes_to_exit(game_in_menu):
    response = game_in_menu.handle_action(Quit())
    assert response.screen is Screen.EXIT


def test_new_game_outside_menu_is_ignored(game_in_menu):
    game_in_menu.handle_action(NewGame())             # menu -> création
    response = game_in_menu.handle_action(NewGame())  # hors contexte
    assert response.screen is Screen.CREATION         # on reste en création


def test_unknown_action_raises(game_in_menu):
    class UnknownAction(Action):
        pass

    with pytest.raises(ValueError):
        game_in_menu.handle_action(UnknownAction())