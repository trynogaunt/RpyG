"""Pilote le vrai écran d'inventaire Textual en mode headless."""
import asyncio
from pathlib import Path

import pytest

from core import boot as boot_module
from core.boot import Boot
from core.game.actions import ConfirmCreation, NewGame, SetName
from core.game.I18n import Translation
from core.items.base import ItemInstance
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


def run_inventory(scenario):
    """Crée un personnage avec une épée et un bouclier, ouvre l'inventaire avec `i`, puis joue `scenario`."""
    async def main():
        app = TextualApp(Boot(Settings(), DATA_DIR), Translation(locales="fr", locales_dir=DATA_DIR / "lang"), Settings())
        async with app.run_test(size=(130, 32)) as pilot:
            await pilot.pause(0.3)
            for action in (NewGame(), SetName("Bob"), ConfirmCreation()):
                app.dispatch(action)
                await pilot.pause(0.1)
            shield = app.game.catalog.get("wooden_shield")
            app.game.player.inventory.add(shield, instance=ItemInstance("wooden_shield", wear=0.4))
            await pilot.press("i")
            await pilot.pause(0.3)
            return await scenario(app, pilot)
    return asyncio.run(main())


def worn(app) -> list[str]:
    return [e.item_id for e in app.game.player.inventory.equipment if e.item_id]


def test_i_opens_inventory_screen():
    async def scenario(app, pilot):
        return type(app.screen).__name__
    assert run_inventory(scenario) == "InventoryScreen"


@pytest.mark.parametrize("button", [1, 3], ids=["clic gauche", "clic droit"])
def test_click_shows_item_without_equipping_it(button):
    async def scenario(app, pilot):
        await pilot.click("#inv-bag", offset=(3, 1), button=button)
        await pilot.pause(0.3)
        return app.screen.query_one("#inv-detail-panel").border_title, worn(app)
    title, equipped = run_inventory(scenario)
    assert title == "Bouclier en Bois"
    assert equipped == []


def test_enter_equips_highlighted_item():
    async def scenario(app, pilot):
        await pilot.press("tab")
        await pilot.pause(0.2)
        await pilot.press("enter")
        await pilot.pause(0.3)
        return worn(app)
    assert run_inventory(scenario) == ["wooden_sword"]


def test_escape_closes_inventory():
    async def scenario(app, pilot):
        await pilot.press("escape")
        await pilot.pause(0.3)
        return type(app.screen).__name__
    assert run_inventory(scenario) == "ExplorationScreen"
