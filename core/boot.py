"""Chargement du jeu, étape par étape, indépendamment de l'interface.

Chaque interface affiche son propre écran de chargement en appelant `Boot.run()`
avec un callback de progression, puis récupère le jeu avec `Boot.build_game()`.
"""
import logging
import threading
import time
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from collections.abc import Callable

from core.game.game import Game
from core.items.catalog import ItemCatalog
from core.items.item_loader import load_catalog
from core.save.store import SaveStore
from core.updater import UpdateStatus, check
from core.world.loader import load_world

log = logging.getLogger(__name__)

DISCORD_APP_ID = "1439725986290860132"
UPDATE_TIMEOUT = 3.0      


class StepStatus(Enum):
    RUNNING = auto()
    DONE = auto()
    UNAVAILABLE = auto()   
    TIMEOUT = auto()     


@dataclass(frozen=True)
class BootStep:
    key: str                             
    run: Callable[[], StepStatus]


ProgressCallback = Callable[[int, BootStep, StepStatus], None]


class Boot:
    def __init__(self, settings, data_dir: Path, step_delay: float = 0.0):
        self.settings = settings
        self.data_dir = data_dir
        self.step_delay = step_delay      # pause après chaque étape (captures d'écran, démos)
        self.catalog: ItemCatalog | None = None
        self.world = None
        self.presence = None
        self.update: UpdateStatus | None = None
        self.game: Game | None = None

    def steps(self) -> list[BootStep]:
        steps = [
            BootStep("items", self._load_items),
            BootStep("world", self._load_world),
        ]
        if self.settings.discord_integration:
            steps.append(BootStep("discord", self._connect_discord))
        steps.append(BootStep("updates", self._check_updates))
        return steps

    def run(self, on_progress: ProgressCallback = lambda *_: None) -> None:
        for index, step in enumerate(self.steps()):
            on_progress(index, step, StepStatus.RUNNING)
            status = step.run()
            log.info("boot: %s -> %s", step.key, status.name)
            on_progress(index, step, status)
            if self.step_delay:
                time.sleep(self.step_delay)

    def build_game(self) -> Game:
        self.game = Game(world=self.world, store=SaveStore(), settings=self.settings,
                         catalog=self.catalog, update=self.update)
        return self.game

    def _load_items(self) -> StepStatus:
        self.catalog = load_catalog()
        return StepStatus.DONE

    def _load_world(self) -> StepStatus:
        self.world = load_world(data_dir=self.data_dir)
        return StepStatus.DONE

    def _connect_discord(self) -> StepStatus:
        from core.integrations.discord import DiscordIntegration
        presence = DiscordIntegration(app_id=DISCORD_APP_ID)
        presence.connect()
        if not presence.connected:
            return StepStatus.UNAVAILABLE
        self.presence = presence
        return StepStatus.DONE

    def _check_updates(self) -> StepStatus:
        def worker():
            self.update = check()
            if self.game is not None:   
                self.game.update = self.update

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        thread.join(timeout=UPDATE_TIMEOUT)
        if thread.is_alive():
            return StepStatus.TIMEOUT
        return StepStatus.DONE if self.update is not None else StepStatus.UNAVAILABLE
