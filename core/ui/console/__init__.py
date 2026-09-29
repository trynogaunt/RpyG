from core.ui.console.app import ConsoleApp

def run(game, translation=None, settings=None) -> None:
    ConsoleApp(game, translation=translation, settings=settings).run()