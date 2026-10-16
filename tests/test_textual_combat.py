"""Combat dans l'interface Textual : du bassin de la grotte jusqu'à la victoire ou au game over."""
import asyncio
from random import Random
from pathlib import Path

import pytest

from core import boot as boot_module
from core.boot import Boot
from core.enums import Direction
from core.game.actions import ConfirmCreation, Move, NewGame, SetName
from core.game.I18n import Translation
from core.ui.textual.app import TextualApp
from core.updater import UpdateState, UpdateStatus

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


class Settings:
    locale = "fr"
    discord_integration = False
    interface = "textual"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(boot_module, "check", lambda: UpdateStatus(UpdateState.UP_TO_DATE))


class NoCrit(Random):
    def random(self) -> float:
        return 0.99


def run_at_rat(scenario):
    """Crée un personnage, descend jusqu'au bassin (où vit le rat), puis joue `scenario`."""
    async def main():
        app = TextualApp(Boot(Settings(), DATA_DIR), Translation(locales="fr", locales_dir=DATA_DIR / "lang"), Settings())
        async with app.run_test(size=(100, 24)) as pilot:
            await pilot.pause(0.3)
            app.game.rng = NoCrit()                      # jets fixes : pas de critique
            for action in (NewGame(), SetName("Bob"), ConfirmCreation(),
                           Move(Direction.SOUTH), Move(Direction.SOUTH), Move(Direction.SOUTH)):
                app.dispatch(action)
                await pilot.pause(0.1)
            return await scenario(app, pilot)
    return asyncio.run(main())


def screen_name(app) -> str:
    return type(app.screen).__name__


def test_fight_until_victory():
    async def scenario(app, pilot):
        await pilot.press("c")
        await pilot.pause(0.2)
        names = [screen_name(app)]
        for _ in range(3):
            await pilot.press("a")
            await pilot.pause(0.2)
        names.append(screen_name(app))
        return names
    assert run_at_rat(scenario) == ["CombatScreen", "ExplorationScreen"]


def test_flee_returns_to_exploration():
    async def scenario(app, pilot):
        await pilot.press("c")
        await pilot.pause(0.2)
        await pilot.press("f")
        await pilot.pause(0.2)
        return screen_name(app), app.game.combat
    assert run_at_rat(scenario) == ("ExplorationScreen", None)


def test_defeat_shows_game_over_then_main_menu():
    async def scenario(app, pilot):
        app.game.player.health = 1
        await pilot.press("c")
        await pilot.pause(0.2)
        await pilot.press("a")
        await pilot.pause(0.3)
        names = [screen_name(app)]
        await pilot.press("escape")
        await pilot.pause(0.3)
        names.append(screen_name(app))
        return names
    assert run_at_rat(scenario) == ["GameOverScreen", "MainMenuScreen"]
