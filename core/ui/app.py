from textual.app import App as Tapp

class App(Tapp):
    def __init__(self, game, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game