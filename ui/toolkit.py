import textwrap
import os
from typing import List
from enum import Enum
import re

class Colors(str, Enum):
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    LIGHT_GRAY = "\033[38;5;250m"
    
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def len_visible(text: str) -> int:
    """Retourne la longueur du texte sans les codes couleurs invisibles."""
    return len(ANSI_ESCAPE.sub('', text))


def color_text(text:str, color_code:str) -> str:
    return f"{color_code}{text}\033[0m"

def splash(width: int, border_char: str) -> List[str]:

    R = [
        "██████╗",
        "██╔══██╗",
        "██║  ██║",
        "██████╔╝",
        "██╔══██╗",
        "██║  ██║",
        "╚═╝  ╚═╝",
    ]

    P = [
        "██████╗",
        "██╔══██╗",
        "██████╔╝",
        "██╔═══╝ ",
        "██║     ",
        "██║     ",
        "╚═╝     ",
    ]

    Y = [
        "██╗   ██╗",
        "╚██╗ ██╔╝",
        " ╚████╔╝ ",
        "  ╚██╔╝  ",
        "   ██║   ",
        "   ██║   ",
        "   ╚═╝   ",
    ]

    G = [
        " ██████╗",
        "██╔════╝",
        "██║  ███╗",
        "██║   ██║",
        "██║   ██║",
        "╚██████╔╝",
        " ╚═════╝ ",
    ]

    slogan = color_text("Your CPU will handle all the dragons", Colors.LIGHT_GRAY.value)

    # largeurs fixes par lettre
    wR = max(len(line) for line in R)
    wP = max(len(line) for line in P)
    wY = max(len(line) for line in Y)
    wG = max(len(line) for line in G)

    spacing = 3
    logo_width = wR + spacing + wP + spacing + wY + spacing + wG
    
    
    padding_left = max(0, (width - logo_width) // 2)
    indent = " " * padding_left
    
    lines: List[str] = []
    for i in range(len(R)):
        line = (
            f"{indent}"  
            f"{color_text(R[i].ljust(wR), Colors.WHITE.value)}   "
            f"{color_text(P[i].ljust(wP), Colors.YELLOW.value)}   "
            f"{color_text(Y[i].ljust(wY), Colors.YELLOW.value)}   "
            f"{color_text(G[i].ljust(wG), Colors.WHITE.value)}"
        )
        lines.append(line)

    lines.append("")      # petite ligne vide
    slogan_line = center_text(slogan, width, " ")
    lines.extend(slogan_line)
    return lines

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def header(text:str, width:int, border_char:str, h_char:str) -> List[str]:
    h_border = h_char * width
    centered = center_text(text, width, border_char)
    return [h_border] + centered + [h_border]

def sub_header(text: str, width:int) -> List[str]:
        round_text = f"{text}"
        return [f"{round_text.center(width, "-")}" ]

def bottom_bar(width:int, h_char:str) -> List[str]:
    h_border = h_char * width
    return [h_border] 
    
def center_text(text:str, width:int, border_char:str=" ") -> List[str]:
    visible_length = len_visible(text)
    total_padding =  (width - 2) - visible_length
     
    if total_padding < 0:
        total_padding = 0
    left_padding = total_padding // 2
    right_padding = total_padding - left_padding
    text = border_char + " " * left_padding + text.strip() + " " * right_padding + border_char
    return [text]

def text_block(text:str, width:int,indent:int=0, border_char:str=" ") -> List[str]:
    """
    Affiche un paragraphe mis en forme selon la largeur du UI, autowrappé.
    
    :param text: Le texte à afficher
    :param width: La largeur totale du UI
    :param indent: Le nombre d'espaces à ajouter au début de chaque ligne
    :param border_char: Le caractère à utiliser pour les bordures (par défaut un espace)
    :returns: Une liste de lignes formatées prêtes à être affichées
    """
    
    inner_width = width - 2
    wrapped_text = textwrap.fill(text, width=inner_width - indent)
    lines = [f"{border_char}{' ' * indent}{line.ljust(inner_width - indent)}{border_char}" for line in wrapped_text.splitlines()]
    return lines

def message_box(message:str, width:int, border_char:str, padding:int) -> List[str]:
    inner_width = width - 2
    border = border_char * width
    wrapped_text = textwrap.fill(message, width=inner_width - padding * 2)
    padded_lines = [f"{border_char}{' ' * padding}{line.ljust(inner_width - padding * 2)}{' ' * padding}{border_char}" for line in wrapped_text.splitlines()]
        
    return [border] + padded_lines + [border]

def health_bar(current:int, maximum:int, bar_length:int=20) -> str:
    """Retourne une représentation textuelle de la barre de santé."""
    health_ratio = current / maximum
    filled_length = int(bar_length * health_ratio)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    return f"{bar}"

def format_hp(current:int, maximum:int) -> str:
    return f"({current}/{maximum})"

def compute_health_bar(col_width:int, left_part: str, hp_text:str)-> int:
    static_len = len(left_part) + len(hp_text) + 1 
    available = col_width - static_len
    return max(5, min(available, 20)) # taille min/max entre 5 et 20

def empty_line(count:int = 1, width:int = 0, border_char:str = " ") -> List[str]:
    lines = []
    for _ in range(count):
        if width > 0:
            inner_space = " " * (width - 2)
            lines.append(f"{border_char}{inner_space}{border_char}")
        else:
            lines.append("")
    return lines