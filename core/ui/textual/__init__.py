from core.ui.textual.app import TextualApp

def run(game, translation=None, settings=None) -> None:
    TextualApp(game, translation=translation, settings=settings).run()