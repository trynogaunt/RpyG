from ui_console import show_combat_ui, log_attack, show_victory, show_defeat
from dataclasses import dataclass
from typing import Literal
from classes.hero import Hero
from classes.ennemy import Enemy
from classes.interface_class import ActionCombatChoice, ActionType
@dataclass
class CombatLog:
    message: str

class Combat:
    def __init__(self, hero: Hero, enemies: list[Enemy]):
        self.hero: Hero = hero
        self.enemies : list[Enemy]= enemies
        self.log: list[CombatLog] = []
        self.combatants: list = [hero] + enemies
        self.round_number: int = 1
        self.turn_index: int = 0
        self.actions: list[ActionCombatChoice] = []
        self.is_finished: bool = False
        self.current_combatant = None

    def run(self):
        self.determine_initial_turn_order()
        while not self.is_finished:
            self.current_combatant = self.get_current_combatant()
            if self.current_combatant == self.hero:
                self.hero_phase()
            else:
                self.enemy_phase(self.current_combatant)
            self.turn_index += 1
        if not self.check_combat_end():
            self.round_number += 1
            self.turn_index = 0
            self.recalculate_turn_order()
    
    def determine_initial_turn_order(self):
        self.combatants = sorted(self.combatants, key=lambda c: c.speed, reverse=True)
    
    def recalculate_turn_order(self):
        already_played = self.combatants[:self.turn_index + 1]
        yet_to_play = self.combatants[self.turn_index + 1:]
        yet_to_play = sorted(yet_to_play, key=lambda c: c.speed, reverse=True)
        self.combatants = already_played + yet_to_play

    def hero_phase(self):
        choice = show_combat_ui(self.hero, self.enemies, [log.message for log in self.log], self.actions)

    def enemy_phase(self, enemy: Enemy):
        damage = enemy.attack(self.hero)
        log_entry = log_attack(enemy, self.hero, damage)
        self.log.append(CombatLog(log_entry))
    
    def check_combat_end(self):
        if not self.hero.is_alive():
            self.is_finished = True
            show_defeat()
            return True
        elif all(not enemy.is_alive() for enemy in self.enemies):
            self.is_finished = True
            loot = []
            for enemy in self.enemies:
                loot.extend(enemy.inventory.items)
            show_victory(self.hero, enemy, loot)
            return True
        return False

    @property
    def get_current_combatant(self):
        return self.turn_order[self.turn_index]
    
    @property
    def actors(self):
        return self.combatants
