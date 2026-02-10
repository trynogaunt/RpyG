import questionary
from ui import toolkit as tk
from events.response import GameResponse, ResponseType
from ui.screens import main_menu_screen, creation_screen, room_screen, inventory_screen, combat_screen
from models.game_context import GameContext
from typing import Dict

class UIController:
    def __init__(self, ctx: GameContext, width=80, border_char="|",header_char="=", padding=0):
        if width < 70:
            width = 70  
        self.width = width
        self.border_char = border_char
        self.header_char = header_char
        self.padding = padding
        self.ctx = ctx
    
    def choose(self, prompt:str, choices:list[str|tuple], value=None) -> str:
        if isinstance(choices[0], tuple):
            choices = [questionary.Choice(title=title, value=val) for title, val in choices]
        if isinstance(choices[0], str):
            choices = [questionary.Choice(title=title, value=title) for title in choices]
        return questionary.select(
            prompt,
            choices=choices
        ).ask()
            
    def confirm(self, prompt:str) -> bool:
        return questionary.confirm(prompt).ask()

    def ask_text(self, prompt:str) -> str:
        return questionary.text(prompt).ask()
    
    def render(self, response: GameResponse):
        tk.clear()
        match response.type:
            case ResponseType.MAIN_MENU:
                lines = main_menu_screen.render(self, response)
            case ResponseType.CHARACTER_CREATION:
                lines = creation_screen.render(self, response)
            case ResponseType.IN_COMBAT:
                lines = combat_screen.render(self, response)
            case ResponseType.EXPLORATION:
                 lines = room_screen.render(self, response)
            case ResponseType.ROOM_ENTERED:
                lines = room_screen.render(self, response)
            case ResponseType.SYSTEM:
                match response.payload.get("screen"):
                    case "character_creation":
                        lines = creation_screen.render(self, response)
            case ResponseType.INVENTORY:
                lines = inventory_screen.render(self, response)
            case _:
                lines = ["Unknown response type."]
        for line in lines:
            print(line)
        
        return lines
            
if __name__ == "__main__":
    ui = UIController()
    ui.header("Welcome to the Game")
    ui.message_box("This is a message box. It can display multiple lines of text wrapped and padded nicely within a bordered box.")
    ui.text_block("Here is a simple text block that demonstrates how text can be wrapped according to the UI width settings. This helps in maintaining readability across different terminal sizes.")