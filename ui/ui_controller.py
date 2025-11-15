import os
import textwrap
import questionary

class UIController:
    def __init__(self, width=60, border_char="=", padding=2):
        self.width = width
        self.border_char = border_char
        self.padding = padding
    
    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")
    
    def header(self, title:str):
        self.clear()
        inner_width = self.width - 2
        border = self.border_char * self.width
        text = f"""|{title.center(inner_width)}|"""
        print(border)
        print(text)
        print(border)
    
    def text_block(self, text:str, wrap=True, indent=0):
        """Affiche un paragraphe mis en forme selon la largeur du UI."""
        if wrap:
            wrapped = textwrap.fill(
                text,
                width=self.width - 2,  # garde un peu d'air avec les bords
                subsequent_indent=" " * indent
            )   
            print(wrapped)
        else:
            print(message)

    def message_box(self, message:str):
        self.clear()
        inner_width = self.width - 2
        border = self.border_char * self.width
        wrapped_text = textwrap.fill(message, width=inner_width - self.padding * 2)
        padded_lines = [f"|{' ' * self.padding}{line.ljust(inner_width - self.padding * 2)}{' ' * self.padding}|" for line in wrapped_text.splitlines()]
        
        print(border)
        for line in padded_lines:
            print(line)
        print(border)

    def select_option(self, prompt:str, options:list[str]) -> str:
        """Affiche un menu de sélection et retourne l'option choisie."""
        choice = questionary.select(
            prompt,
            choices=options
        ).ask()
        return choice
        
if __name__ == "__main__":
    ui = UIController()
    ui.header("Welcome to the Game")
    ui.message_box("This is a message box. It can display multiple lines of text wrapped and padded nicely within a bordered box.")
    ui.text_block("Here is a simple text block that demonstrates how text can be wrapped according to the UI width settings. This helps in maintaining readability across different terminal sizes.")