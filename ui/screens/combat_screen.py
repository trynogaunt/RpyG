from ui.ui_controller import UIController
from typing import Iterable, List
from classes.character import Character
from classes.interface_class import ActionType
from game.combat import Combat
from collections import Counter
import questionary

ALL_ACTIONS: list[ActionType] = ["Attack", "Defend", "Inventory", "Flee"]

def ennemy_group_label_names(enemies: Iterable["Character"]) -> str:
    enemis = list(enemies)
    if not enemis:
        return "No enemies"
    if len(enemis) == 1:
        return enemis[0].name
    
    def enemy_kind(e):
        return getattr(e, 'kind', getattr(e, 'enemy_type',e.name)).capitalize()
    
    kinds = [enemy_kind(e) for e in enemis]
    counts = Counter(kinds)
    if len(counts) == 1:
        kind = next(iter(counts.keys()))
        count = counts[kind]
        plurial = kind if kind.endswith('s') else kind + 's'
        return f"{plurial} (x{count})".capitalize()
    
    total = len(enemis)
    return f"Enemies group".capitalize()

def combat_header(ui, hero: "Character", enemies: Iterable["Character"]) -> list[str]:
    title = f"{hero.name} vs {ennemy_group_label_names(enemies)}"
    return ui.header(title)


def build_status_section(ui, hero: "Character", enemies: Iterable["Character"]) -> list[str]:
    total_width = ui.width
    col_width = (total_width // 2 ) - 3  # 4 for borders and spacing
    hero_hp_text = ui.format_hp(hero.health, hero.max_health)
    bar_width = ui.compute_health_bar(col_width, f"HP: ", "")
    hero_hp_bar = ui.health_bar(hero.health, hero.max_health, bar_width)
    hero_lines: List[str] = [
        f"{hero.name}",
        f"HP: {hero_hp_bar}",
        f"{hero_hp_text}",
        f"STR: {hero.strength} | SPD: {hero.speed} | LUCK: {hero.luck}",
    ]

    enemy_lines: List[str] = []
    for enemy in enemies:
        enemy_hp_text = ""
        bar_width = ui.compute_health_bar(col_width, f"HP: ", "")
        enemy_hp_bar = ui.health_bar(enemy.health, enemy.max_health, bar_width)
        enemy_lines.append(
            f"{enemy.name}: {enemy_hp_bar}"
        )
        max_rows = max(len(hero_lines), len(enemy_lines)) # Ensure both columns have equal rows
        lines: List[str] = []
    for i in range(max_rows):
        left = hero_lines[i] if i < len(hero_lines) else ""
        right = enemy_lines[i] if i < len(enemy_lines) else ""
            
        left_rendered = left[:col_width].ljust(col_width) # Ensure fixed width
        right_rendered = right[:col_width].ljust(col_width) # Ensure fixed width
        lines.append(f"| {left_rendered}| {right_rendered} |") # Combine columns with borders
    return lines

def build_log_section(ui, logs: List[str], max_lines: int = 5) -> list[str]:
    log_lines = logs[-max_lines:]  # Get the last max_lines entries
    log_content = []
    for entry in log_lines:
        wrapped_entry = ui.text_block(entry, wrap=True, indent=2)
        log_content.extend(wrapped_entry)
    if len(log_content) == 0:
        log_content.append("No combat log entries yet.")
        while len(log_content) < max_lines:
            log_content.insert(1, "")
    elif len(log_content) < max_lines:
        while len(log_content) < max_lines:
            log_content.insert(1, "")
    return log_content

def build_choices_section(actions: List[str]) -> list[str]:
    choice_lines = ["Available Actions:"]
    for idx, action in enumerate(actions, start=1):
        choice_lines.append(f"{idx}. {action}")
    return choice_lines

def build_combat_ui(ui: UIController, combat: Combat) -> list[str]:
    lines = []
    hero = combat.hero
    enemies = combat.enemies
    actions = ALL_ACTIONS
    logs = [log.message for log in combat.log]
    lines.extend(combat_header(ui, hero, enemies))
    lines.extend(ui.sub_header(f" Round {combat.round_number} "))
    lines.append("")  # Empty line for spacing
    lines.extend(build_status_section(ui, hero, enemies))
    lines.append("")  # Empty line for spacing
    lines.extend(ui.sub_header(" Combat Log "))
    lines.extend(build_log_section(ui, logs))
    lines.append("")  # Empty line for spacing
    lines.extend(build_choices_section(actions))

    return lines
    
