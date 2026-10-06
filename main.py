from core.game.game import Game
from core.world.loader import load_world
from pathlib import Path
from core.game.I18n import Translation
from core.game.settings import Settings, default_settings_path
import argparse
import importlib
import logging
from core.save.store import SaveStore
from core.integrations.discord import DiscordIntegration

log = logging.getLogger(__name__)
logging.basicConfig(filename="rpyg.log", level=logging.INFO)

FRONTENDS = {
    "textual": "core.ui.textual",
    "console": "core.ui.console"
}

FALLBACK = "console"

def parse_args():
    parser = argparse.ArgumentParser(prog="rpyg")
    parser.add_argument("--ui", choices=FRONTENDS.keys())
    return parser.parse_args()

def resolve_frontend(cli_choice, settings):
    candidates = [cli_choice, settings.interface, FALLBACK]
    for name in candidates:
        if name not in FRONTENDS:
            continue
        try:
            return importlib.import_module(FRONTENDS[name])
        except ImportError as e:
            raise ImportError(f"Failed to import frontend '{name}'") from e
    raise ImportError("No suitable frontend found.")

def main():
    data_dir = Path(__file__).parent / "data"
    lang_dir = data_dir / "lang"
    args = parse_args()

    # Load settings from the default settings path
    settings = Settings.load(default_settings_path())

    presence = None
    if settings.discord_integration:
        try:
            presence = DiscordIntegration(app_id="1439725986290860132")
            presence.connect()
        except Exception as e:
            print(f"Failed to connect to Discord: {e}")
            presence = None
    
    # Ensure the locale specified in the settings is available
    available = {p.stem for p in lang_dir.glob("*.json")}
    if settings.locale not in available:
        settings.locale = "en"

    # Initialize the translation system with the resolved locale
    translation = Translation(locales_dir=lang_dir, locales=settings.locale)

    # Load the game world from the data directory
    game = Game(world=load_world(data_dir=data_dir), store=SaveStore(), settings=settings)

    # Resolve and initialize the selected frontend - Fallback to console without external libraries if necessary
    log.info("main: discord_integration=%s presence=%r", settings.discord_integration, presence)
    frontend = resolve_frontend(args.ui, settings)
    frontend.run(game, translation=translation, settings=settings, presence=presence)
    


if __name__ == "__main__":
    main()