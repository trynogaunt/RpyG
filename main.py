from core.game.game import Game
from core.ui.app import RpygApp
from core.world.loader import load_world
from pathlib import Path
from core.game.I18n import Translation
from core.game.settings import Settings, default_settings_path
import argparse
import importlib

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
    candidates = [cli_choice, settings.frontend, FALLBACK]
    for name in candidates:
        if name not in FRONTENDS:
            continue
        try:
            return importlib.import_module(FRONTENDS[name])
        except ImportError:
            print(f"Failed to import frontend '{name}'")
    raise ImportError("No suitable frontend found.")

def main():
    data_dir = Path(__file__).parent / "data"
    lang_dir = data_dir / "lang"
    args = parse_args()

    settings = Settings.load(default_settings_path())
    frontend = resolve_frontend(args.ui, settings)
    available = {p.stem for p in lang_dir.glob("*.json")}
    if settings.locale not in available:
        settings.locale = "en"

    translation = Translation(lang_dir, locales=settings.locale)
    game = Game(world=load_world(data_dir=data_dir))
    app = RpygApp(game, translation=translation, settings=settings)
    app.run()


if __name__ == "__main__":
    main()