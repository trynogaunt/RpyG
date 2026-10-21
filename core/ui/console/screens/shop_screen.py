from core.ui.console.screens.base_screen import BaseConsoleScreen, pad

class ShopScreen(BaseConsoleScreen):

    def draw(self) -> None:
        self.rule()
        print( "Shop")
        self.rule()

    def ask(self):
        pass
