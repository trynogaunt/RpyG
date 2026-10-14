from unittest.mock import patch

import pytest

from core.game.actions import Back, LoadGame, Quit
from core.ui.console.screens.base_screen import BaseConsoleScreen


class FakeApp:
    def t(self, key, **params):
        return key


class Screen(BaseConsoleScreen):
    def draw(self): ...
    def ask(self): ...


@pytest.fixture
def screen():
    return Screen(FakeApp())


def choose(screen, options, *inputs):
    with patch("builtins.input", side_effect=inputs):
        return screen.choose(options)


OPTIONS = [("Retour", Back()), ("Slot 1", LoadGame(1)), ("Slot 2", LoadGame(2))]


def test_back_is_on_zero_wherever_it_is_listed(screen):
    assert choose(screen, OPTIONS, "0") == Back()


def test_other_options_are_numbered_from_one_without_back(screen):
    assert choose(screen, OPTIONS, "1") == LoadGame(1)
    assert choose(screen, OPTIONS, "2") == LoadGame(2)


def test_back_is_printed_last_on_zero(screen, capsys):
    choose(screen, OPTIONS, "0")
    lines = capsys.readouterr().out.splitlines()
    assert lines == ["  1. Slot 1", "  2. Slot 2", "  0. Retour"]


def test_quit_goes_on_zero_when_there_is_no_back(screen):
    options = [("Quitter", Quit()), ("Nouvelle partie", LoadGame(1))]
    assert choose(screen, options, "0") == Quit()
    assert choose(screen, options, "1") == LoadGame(1)


def test_back_wins_over_quit(screen):
    options = [("Quitter", Quit()), ("Retour", Back())]
    assert choose(screen, options, "0") == Back()
    assert choose(screen, options, "1") == Quit()


def test_zero_is_invalid_without_exit_option(screen):
    assert choose(screen, [("Slot 1", LoadGame(1))], "0", "1") == LoadGame(1)


def test_out_of_range_is_rejected(screen):
    assert choose(screen, OPTIONS, "3", "1") == LoadGame(1)
