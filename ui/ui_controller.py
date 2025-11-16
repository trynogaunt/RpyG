import os
import textwrap
import questionary
import time

class UIController:
    def __init__(self, width=80, border_char="=", padding=2):
        if width < 70:
            width = 70  
        self.width = width
        self.border_char = border_char
        self.padding = padding
    
    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")
    
    def header(self, title:str):
        inner_width = self.width - 2
        border = self.border_char * self.width
        text = f"""|{title.center(inner_width)}|"""
        return [border, text, border]
    
    def sub_header(self, text: str) -> list[str]:
        round_text = f"{text}"
        return [f"{round_text.center(self.width, "-")}" ]
    
    def text_block(self, text:str, wrap=True, indent=0):
        """Affiche un paragraphe mis en forme selon la largeur du UI."""
        if wrap:
            wrapped = textwrap.fill(
                text,
                width=self.width - 2, 
                subsequent_indent=" " * indent
            )   
            print(wrapped)
        else:
            print(message)

    def message_box(self, message:str):
        inner_width = self.width - 2
        border = self.border_char * self.width
        wrapped_text = textwrap.fill(message, width=inner_width - self.padding * 2)
        padded_lines = [f"|{' ' * self.padding}{line.ljust(inner_width - self.padding * 2)}{' ' * self.padding}|" for line in wrapped_text.splitlines()]
        
        return [border] + padded_lines + [border]

    def select_option(self, prompt:str, options:list[str]) -> str:
        """Affiche un menu de sélection et retourne l'option choisie."""
        choice = questionary.select(
            prompt,
            choices=options
        ).ask()
        return choice

    def health_bar(self, current:int, maximum:int, bar_length:int=20) -> str:
        """Retourne une représentation textuelle de la barre de santé."""
        health_ratio = current / maximum
        filled_length = int(bar_length * health_ratio)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        return f"{bar}"
    
    def format_hp(self, current:int, maximum:int) -> float:
        return f"({current}/{maximum})"
    
    def compute_health_bar(self, col_width:int, left_part: str, hp_text:str)-> int:
        static_len = len(left_part) + len(hp_text) + 1 
        available = col_width - static_len
        return max(5, min(available, 20)) # taille min/max entre 5 et 20

    def empty_line(self):
        print("")
    
    def render(self, lines: list[str], tick_render: float = 0, clear_before: bool = True, center: bool = False):
        if clear_before:
            self.clear()
        for line in lines:
            if center:
                line = line.center(self.width)
            time.sleep(tick_render)
            print(line)

if __name__ == "__main__":
    ui = UIController()
    ui.header("Welcome to the Game")
    ui.message_box("This is a message box. It can display multiple lines of text wrapped and padded nicely within a bordered box.")
    ui.text_block("Here is a simple text block that demonstrates how text can be wrapped according to the UI width settings. This helps in maintaining readability across different terminal sizes.")