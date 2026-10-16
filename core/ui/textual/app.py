from textual.app import App 
from textual.screen import Screen
from pathlib import Path

from core.game.response import GameResponse
from core.game.I18n import Translation
from core.enums import Screens
from core.ui.textual.screens.main_menu import MainMenuScreen
from core.ui.textual.screens.creation import CreationScreen
from core.ui.textual.screens.exploration import ExplorationScreen
from core.ui.textual.screens.slot_screen import SlotsScreen
from core.ui.textual.screens.options_screen import OptionsScreen
from core.ui.textual.screens.loading import LoadingScreen
from core.ui.textual.screens.inventory_screen import InventoryScreen
from core.ui.textual.screens.catalog_screen import CatalogScreen
from core.ui.textual.widgets.discord_indicator import DiscordIndicator
from core.integrations.discord import presence_for

import logging
log = logging.getLogger(__name__)

class TextualApp(App):

    CSS_PATH = Path("rpyg.tcss")
    def __init__(self, boot, translation, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.boot = boot
        self.game = None                  # construit à la fin de l'écran de chargement
        self.translation = translation
        self.settings = settings
        self.presence = None
        self.current_screen_id: Screens | None = None
        self.all_screens = {
            Screens.MAIN_MENU: MainMenuScreen,
            Screens.CREATION: CreationScreen,
            Screens.EXPLORATION: ExplorationScreen,
            Screens.SLOTS: SlotsScreen,
            Screens.OPTIONS: OptionsScreen,
            Screens.INVENTORY: InventoryScreen,
            Screens.CATALOG: CatalogScreen,
        }

    def _sync_translation(self) -> None:
        if self.translation.locale_file != self.settings.locale:
            self.translation = Translation(locales=self.settings.locale, locales_dir=self.translation.locales_dir)

    def build_screen(self, screen_id: Screens, view=None) -> Screen:
        log.info("build_screen %s view=%r", screen_id, view)
        screen_class = self.all_screens.get(screen_id)
        if screen_class:
            return screen_class(view=view)
        else:
            raise ValueError(f"No screen found for {screen_id}")

    def t(self, key: str, **params) -> str:
        return self.translation.t(key, **params)

    def on_mount(self):
        self.push_screen(LoadingScreen(self.boot))

    def start_game(self) -> None:
        """Appelé par l'écran de chargement une fois toutes les étapes terminées."""
        self.game = self.boot.build_game()
        self.presence = self.boot.presence
        if self.presence:
            self._discord_connected = self.presence.connected
            self.set_interval(2, self._watch_discord)
        self.show(self.game.start())

    def _watch_discord(self) -> None:
        """Rafraîchit l'indicateur et prévient quand la liaison Discord change."""
        connected = self.presence.connected
        if connected != self._discord_connected:
            self._discord_connected = connected
            if connected:
                self.notify(self.t("ui.discord.restored"), timeout=4)
            else:
                self.notify(self.t("ui.discord.lost"), severity="warning", timeout=6)
        for indicator in self.screen.query(DiscordIndicator):
            indicator.refresh_status()

    def dispatch(self, action):
        response = self.game.handle_action(action)
        self._sync_translation()
        log.info("dispatch %r -> screen=%s view=%r", action, response.screen, response.view)
        self.show(response)
    
    def show(self, response):
        if response.screen is Screens.EXIT:
            if self.presence:
                self.presence.close()
            self.exit()
            return
        if response.screen is self.current_screen_id:
            self.screen.update_view(response.view)
            self.screen.show_messages(response.messages)
        else:
            self.current_screen_id = response.screen
            screen = self.build_screen(response.screen, response.view)
            self.switch_screen(screen)
            if self.presence:
                screen.call_after_refresh(screen.mount, DiscordIndicator())
            # Le nouvel écran n'est pas encore composé : on attend son premier rafraîchissement
            screen.call_after_refresh(screen.show_messages, response.messages)
    
        if self.presence:
            self.presence.update(presence_for(response, self.t))
    
    def resolve_message(self, translation, message) -> str:
        text = translation.t(message.key, **message.params)
        if text == message.key and message.fallback_key:
            text = translation.t(message.fallback_key, **message.params)
        return text