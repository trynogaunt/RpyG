from core.enums import Screens
from core.ui.console.screens.main_menu import MainMenuScreen
from core.ui.console.screens.creation import CreationScreen
from core.ui.console.screens.exploration import ExplorationScreen
from core.ui.console.screens.slot_screen import SlotScreen
from core.ui.console.screens.options import OptionsScreen
from core.game.I18n import Translation
import logging
log = logging.getLogger(__name__)

class ConsoleApp:
    def __init__(self, game, translation: Translation, settings, presence):
        self.game = game
        self.translation = translation
        self.settings = settings
        self.presence = presence
        self.current_screen_id: Screens | None = None
        self.screen = None
        self.running = False
        self.all_screens = {
            Screens.MAIN_MENU: MainMenuScreen,
            Screens.CREATION: CreationScreen,
            Screens.EXPLORATION: ExplorationScreen,
            Screens.SLOTS: SlotScreen,
            Screens.OPTIONS: OptionsScreen,
        }

    def presence_for(self, response, t):
        match response.screen:
            case Screens.MAIN_MENU | Screens.SLOTS | Screens.OPTIONS:
                return t("ui.presence.main_menu"), None
            case Screens.CREATION:
                return t("ui.presence.creation"), None
            case Screens.EXPLORATION:
                v = response.view
                room = t(f"zones.{v.zone_id}.rooms.{v.room_id}.name")
                level = t("ui.presence.level", level=v.player_summary.level)
                return t("ui.presence.exploring", room=room), level
            case _:
                return None, None

    def _sync_translation(self) -> None:
        if self.translation.locale_file != self.settings.locale:
            self.translation = Translation(locales=self.settings.locale, locales_dir=self.translation.locales_dir)

    def build_screen(self, screen_id, view=None):
        screen_class = self.all_screens.get(screen_id)
        if screen_class is None:
            raise ValueError(f"No screen found for {screen_id}")
        return screen_class(app=self, view=view)

    def t(self, key, **params):
        return self.translation.t(key, **params)

    def run(self):                       # ≈ on_mount + la boucle d'événements de Textual
        self.running = True
        self.show(self.game.start())
        while self.running:
            action = self.screen.ask()   # la seule vraie différence
            self.dispatch(action)

    def dispatch(self, action):          # identique
        self.show(self.game.handle_action(action))

    def show(self, response):
        self._sync_translation()
        if response.screen is Screens.EXIT:
            self.running = False
            if self.presence:
                self.presence.close()
            return
        if response.screen is self.current_screen_id:
            self.screen.update_view(response.view)
        else:
            self.current_screen_id = response.screen
            self.screen = self.build_screen(response.screen, response.view)
        self.screen.render(response.messages)
        log.info("show: screen=%s presence=%r", response.screen, self.presence)
        info = self.presence_for(response, self.t)
        log.info("presence_for -> %r", info)
        if self.presence and info:
            self.presence.update(*info)
    
    def resolve_message(self, message) -> str:
        text = self.translation.t(message.key, **message.params)
        if text == message.key and message.fallback_key:
            text = self.translation.t(message.fallback_key, **message.params)
        return text