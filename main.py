from core.game.game import Game
from core.ui.app import RpygApp
from core.world.loader import load_world
from pathlib import Path

def main():
    data_dir = Path(__file__).parent / "data"
    game = Game(world=load_world(data_dir=data_dir))

    app = RpygApp(game)
    app.run()


if __name__ == "__main__":
    main()