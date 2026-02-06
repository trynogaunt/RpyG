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

def ljust_visible(text: str,indent:int, width: int, fillchar: str = " ") -> str:
    """Version de ljust qui ignore les codes ANSI pour le calcul de longueur."""
    if not isinstance(indent, int) or indent < 0:
        indent = 0
    vis_len = len_visible(text) + indent
    padding = max(1, width - vis_len)
    return " " * indent + text + fillchar * padding

def center_visible(text: str, indent:int, width: int, fillchar: str = " ") -> str:
    """Version de center qui ignore les codes ANSI pour le calcul de longueur."""
    if not isinstance(indent, int) or indent < 0:
        indent = 0
    vis_len = len_visible(text) + indent
    total_padding = max(0, width - vis_len)
    left_padding = total_padding // 2
    right_padding = total_padding - left_padding
    return " " * indent + fillchar * left_padding + text + fillchar * right_padding


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

def sub_header(text: str, width:int, indent:int=0, center_char:str="-", border_char:str="") -> List[str]:
        round_text = f"{text}"
        if border_char:
            return [f"{border_char}{round_text.center(width - 2, center_char)}{border_char}" ]
        return [f"{round_text.center(width, center_char)}" ]

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

def left_text(text:str, width:int, border_char:str=" ") -> List[str]:
    visible_length = len_visible(text)
    padding = max(0, (width - 2) - (visible_length + 1))
    text = border_char + " " + text.strip() + " " * padding + border_char
    return [text]

def right_text(text:str, width:int, border_char:str=" ") -> List[str]:
    visible_length = len_visible(text)
    padding = max(0, (width - 2) - (visible_length + 1))
    text = border_char + " " * padding + text.strip() +  " " + border_char
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

def two_column(left_lines: List[str], right_lines: List[str], width:int, border_char:str, col_width:tuple = (50,50), separator:str="|", indent:int=0, linked:bool=False) -> List[str]:
    """
    Affiche deux colonnes côte à côte, avec une largeur totale définie.
    :param left_lines: Les lignes à afficher dans la colonne de gauche
    :param right_lines: Les lignes à afficher dans la colonne de droite
    :param width: La largeur totale du UI
    :param border_char: Le caractère à utiliser pour les bordures
    :param col_width: Un tuple indiquant le pourcentage de largeur pour chaque colonne (par défaut 50/50)
    :param separator: Le caractère à utiliser pour séparer les colonnes (par défaut "|")
    :returns: Une liste de lignes formatées prêtes à être affichées
    """
    
    inner_width = width - (len(border_char)*2 + len(separator) + indent*2) # Calcule de l'espace disponible après les bordures et le séparateur et les espaces
    
    if sum(col_width) != 100: # Si les pourcentages ne font pas 100, on les ignore et on utilise une largeur égale
        total_width = 100
    else:
        total_width = sum(col_width)
    
    # Calcule de la largeur de chaque colonne en fonction des pourcentages et de l'espace disponible    
    l_width = int((col_width[0] / total_width) * inner_width)
    r_width = int(inner_width - l_width)

    
    
    lines = []
    max_lines = max(len(left_lines), len(right_lines))
    if linked:
        for i in range(max_lines):
            left_part = left_lines[i].strip() if i < len(left_lines) else ""
            right_part = right_lines[i].strip() if i < len(right_lines) else ""
            
            wrap_l = textwrap.wrap(left_part, width=l_width) if left_part else [""]
            wrap_r = textwrap.wrap(right_part, width=r_width) if right_part else [""]
            
            if not wrap_l:
                wrap_l = [""]
            if not wrap_r:
                wrap_r = [""]
            
            row_height = max(len(wrap_l), len(wrap_r))   
            
            for j in range(row_height):
                l_line = wrap_l[j] if j < len(wrap_l) else ""
                r_line = wrap_r[j] if j < len(wrap_r) else "" 
                left_part = ljust_visible(l_line, indent, int(l_width), " ")
                right_part = ljust_visible(r_line, indent, int(r_width), " ")
                line = f"{border_char}{left_part}{separator}{right_part}{border_char}"
                
                # Last resort patch for line without enough spaces, need fixing the root cause later (undetermined, maybe related to ANSI codes or textwrap)
                if len_visible(line) < width:
                    line = line[:-1] + " " * (width - len_visible(line)) + border_char
                lines.append(line)
    else:
        for i in range(max_lines):
            left_part = left_lines[i] if i < len(left_lines) else ""
            right_part = right_lines[i] if i < len(right_lines) else ""
            
            left_part = ljust_visible(left_part, indent, int(l_width), " ")
            right_part = ljust_visible(right_part, indent, int(r_width), " ")
            line = f"{border_char}{left_part}{separator}{right_part}{border_char}"
            
            # Last resort patch for line without enough spaces, need fixing the root cause later (undetermined, maybe related to ANSI codes or textwrap)
            if len_visible(line) < width:
                line = line[:-1] + " " * (width - len_visible(line)) + border_char
            lines.append(line)
    
    return lines