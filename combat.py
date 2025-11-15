from ui_console import show_combat_ui, log_attack, show_victory, show_defeat
from dataclasses import dataclass, Literal
from classes.hero import Hero
from classes.ennemy import Enemy
@dataclass
class CombatLog:
    message: str

class Combat:
    self.hero: Hero = None
    self.ennemies : list[Enemy]= []
    self.log: list[CombatLog] = []
    self.round_number: int = 1
    self.turn_index: int = 0
    self.actions: Literal["attack", "defend", "inventory", "flee"]
    self.is_finished: bool = False
    self.current_combatant = None
    self.turn_order: list = []

    def __init__(self, hero: Hero, enemies: list[Enemy]):
        self.hero = hero
        self.enemies = ennemies
        self.log = []
        self.round_number = 1
        self.is_finished = False
        self.turn_order = self.determine_turn_order()
    def run(self):
        while not self.is_finished:
            self.process_turn()
            self.check_combat_end()
    
    def determine_turn_order(self):
        combatants = [self.hero] + self.enemies
        return sorted(combatants, key=lambda c: c.speed, reverse=True)

    def process_turn(self):
        current_combatant = self.get_current_combatant()
        if isinstance(current_combatant, Hero):
            action = self.get_hero_action()
            self.execute_hero_action(action)
        else:
            self.execute_enemy_action(current_combatant)
        self.advance_turn()
