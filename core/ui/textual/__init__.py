from core.ui.textual.app import TextualApp

def run(game, translation=None, settings=None, presence=None) -> None:
    TextualApp(game, translation=translation, settings=settings, presence=presence).run()