from core.ui.textual.app import TextualApp

def run(boot, translation=None, settings=None) -> None:
    TextualApp(boot, translation=translation, settings=settings).run()