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
        hero = game.hero
        room = hero.current_room
        state = game.state

        if state == GameState.EXPLORING:
            state_text = f"Exploring {room.name}" if room else "Exploring the unknown"
            details = f"{hero.name} – HP {hero.health}/{hero.max_health}"



        self.rpc.update(
            details=details,
            state=state_text,
            start=self.start_time,
            large_image="forest",
            large_text="RPG Adventure Game",
            buttons=[{"label": "View the repository", "url": "https://github.com/trynogaunt/RpyG"}],
        )

    def clear(self):
        self.rpc.clear()


