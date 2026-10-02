from core.ui.console.app import ConsoleApp

def run(game, translation=None, settings=None, presence=None) -> None:
    ConsoleApp(game, translation=translation, settings=settings, presence=presence).run()