from pypresence import Presence
import time
from game.game import GameState


class DiscordPresence:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.rpc = Presence(client_id)
        self.rpc.connect()
        self.start_time = time.time()

    def update(self, game):

        state = game.state.name
        details = ""
        state_text = ""
        hero = None
        if state == GameState.MAIN_MENU.name:
            state_text = "In Main Menu"
            details = "At the Main Menu"
        elif state == GameState.CHARACTER_CREATION.name:
            state_text = "Creating Character"
            details = "Designing a new hero"
        elif state == GameState.EXPLORING.name:
            hero = game.hero
            room = hero.current_room
            zone = hero.current_zone
            state = game.state
            state_text = f"Exploring {room.name}" if room else "Exploring the unknown"
            details = f"{hero.name} – {zone.name}" if zone else f"{hero.name} – Exploring"
        elif state == GameState.IN_BATTLE.name:
            hero = game.hero
            combat = game.current_combat
            enemies = combat.enemies if combat else []
            enemy_names = ", ".join(enemy.name for enemy in enemies)
            state_text = f"In Combat with {enemy_names}" if enemies else "In Combat"
            details = f"{hero.name} – HP {hero.health}/{hero.max_health}"


        self.rpc.update(
            details=details if details else "In Game",
            state=state_text if state_text else "Playing",
            start=self.start_time,
            large_image="forest",
            large_text="RPG Adventure Game",
            buttons=[{"label": "View the repository", "url": "https://github.com/trynogaunt/RpyG"}],
        )

    def close(self):
        self.rpc.clear()


