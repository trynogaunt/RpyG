from core.game.game import Game
from core.ui.app import RpygApp
from core.world.loader import load_world
from pathlib import Path
from core.game.I18n import Translation

def main():
    data_dir = Path(__file__).parent / "data"
    game = Game(world=load_world(data_dir=data_dir))
    translation: Translation = Translation(locales_dir=Path("data/lang"), locales="fr")

    app = RpygApp(game, translation=translation)
    app.run()


if __name__ == "__main__":
    main()