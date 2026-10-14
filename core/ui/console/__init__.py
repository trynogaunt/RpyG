from core.ui.console.app import ConsoleApp
from core.ui.console.screens.loading import LoadingScreen

def run(boot, translation=None, settings=None) -> None:
    app = ConsoleApp(None, translation=translation, settings=settings)
    LoadingScreen(app).load(boot)
    app.game = boot.build_game()
    app.presence = boot.presence
    app.run()
