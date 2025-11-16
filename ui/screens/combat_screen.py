from ..ui_controller import UIController
from game.combat import Combat
from typing import Iterable
from collections import Counter

UI = UIController()

def ennemy_group_label_names(enemies: Iterable["Character"]) -> str:
    ennemis = list(enemies)
    if not ennemis:
        return "No enemies"
    if len(ennemis) == 1:
        return ennemis[0].name
    
    def enemy_kind(e):
        return getattr(e, 'kind', getattr(e, 'enemy_type',e.name)).capitalize()
    
    kinds = [enemy_kind(e) for e in ennemis]
    counts = Counter(kinds)
    if len(counts) == 1:
        kind = next(iter(counts.keys()))
        count = counts[kind]
        plurial = kind if kind.endswith('s') else kind + 's'
        return f"{count} {plurial}".capitalize()
    
    total = len(ennemis)
    return f"Ennemies group".capitalize()

def show_combat_ui(combat: Combat, actions):
    UI.clear()
    hero = combat.hero
    ennemies = combat.enemies
    title = f"{hero.name} vs {ennemy_group_label_names(ennemies)}"
    UI.header(title)
    UI.health_bar(hero.health, hero.max_health)
    
