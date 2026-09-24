from textual.screen import Screen
from textual.widgets import Static, OptionList
from textual.widgets.option_list import Option
from textual import on
from core.game.actions import NewGame, Quit

class MainMenuScreen(Screen):
    
    def compose(self):
        yield Static("Main Menu")
        yield OptionList(
            Option("New Game", id="new_game"),
            Option("Exit", id="exit")
        )
    
    @on(OptionList.OptionSelected)
    def on_option_selected(self, event):
        options = {
            "new_game": NewGame(),
            "exit": Quit()
        }
        option = event.option
        action = options.get(option.id)
        if action:
            self.app.dispatch(action)
        else:
            raise KeyError(f"Unknown option id: {option.id}")