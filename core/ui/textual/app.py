from textual.app import App 
from textual.screen import Screen
from pathlib import Path

from core.game.response import GameResponse
from core.game.I18nsource import Translation
from core.enums import Screens
from core.ui.textual.screens.main_menu import MainMenuScreen
from core.ui.textual.screens.creation import CreationScreen
from core.ui.textual.screens.exploration import ExplorationScreen
from core.ui.textual.screens.slot_screen import SlotsScreen
from core.ui.textual.screens.options_screen import OptionsScreen
from core.integrations.discord import presence_for

import logging
log = logging.getLogger(__name__)

class TextualApp(App):

    CSS_PATH = Path("rpyg.tcss")
    def __init__(self, game, translation, settings, presence=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game
        self.translation = translation
        self.settings = settings
        self.presence = presence
        self.current_screen_id: int = None
        self.presence = presence
        self.all_screens = {
            Screens.MAIN_MENU: MainMenuScreen,
            Screens.CREATION: CreationScreen,
            Screens.EXPLORATION: ExplorationScreen,
            Screens.SLOTS: SlotsScreen,
            Screens.OPTIONS: OptionsScreen,
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
        response = self.game.start()
        self.current_screen_id = response.screen
        self.push_screen(self.build_screen(response.screen, response.view))

    def dispatch(self, action):
        response = self.game.handle_action(action)
        self._sync_translation()
        log.info("dispatch %r -> screen=%s view=%r", action, response.screen, response.view)
        self.show(response)
    
    def show(self, response):
        if response.screen is Screens.EXIT:
            self.exit()
            return
        if response.screen is self.current_screen_id:
            self.screen.update_view(response.view)       
        else:
            self.current_screen_id = response.screen
            self.switch_screen(self.build_screen(response.screen, response.view))
        self.screen.show_messages(response.messages)
    
        if self.presence:
            self.presence.update(presence_for(response, self.t))
    
    def resolve_message(self, translation, message) -> str:
        text = translation.t(message.key, **message.params)
        if text == message.key and message.fallback_key:
            text = translation.t(message.fallback_key, **message.params)
        return text