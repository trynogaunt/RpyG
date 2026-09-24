from core.game.game import Game
from core.ui.app import RpygApp

class Main:
    def __init__(self):
        self.game = Game()

    
    def run(self):
        app = RpygApp(self.game)
        app.run()


if __name__ == "__main__":
    main = Main()
    main.run()