class RpygApp:
    def __init__(self, game, translation=None, settings=None):
        self.game = game
        self.translation = translation
        self.settings = settings

    def run(self):
        print("Running RpygApp in console mode")