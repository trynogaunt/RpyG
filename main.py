from core.game.game import Game
from core.ui.app import RpygApp
from core.world.loader import load_world
from pathlib import Path
from core.game.I18n import Translation
from core.game.settings import Settings, default_settings_path

def main():
    data_dir = Path(__file__).parent / "data"
    lang_dir = data_dir / "lang"

    settings = Settings.load(default_settings_path())
    available = {p.stem for p in lang_dir.glob("*.json")}
    if settings.locale not in available:
        settings.locale = "en"

    translation = Translation(lang_dir, locales=settings.locale)
    game = Game(world=load_world(data_dir=data_dir))
    app = RpygApp(game, translation=translation, settings=settings)
    app.run()


if __name__ == "__main__":
    main()