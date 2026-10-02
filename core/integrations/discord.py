import time
from core.enums import Screens
from pypresence import Presence

class DiscordIntegration:
    MIN_INTERVAL = 15  # minimum interval in seconds between updates

    def __init__(self, app_id):
        self.app_id = app_id
        self._rpc = None
        self._start = int(time.time())
        self._last = 0.0

    def connect(self):
        try:
            self._rpc = Presence(self.app_id)
            self._rpc.connect()
        except Exception as e:
            print(f"Failed to connect to Discord RPC: {e}")
            self._rpc = None
        
    def update_presence(self, details: str, state: str = None) -> None:
        if self._rpc is None or time.monotonic() - self._last < self.MIN_INTERVAL:
            return
        try:
            self._rpc.update(details=details, state=state, start=self._start, large_image="large_image_key")
            self._last = time.monotonic()
        except Exception as e:
            print(f"Failed to update Discord presence: {e}")
            self._rpc = None
    
    def close(self) -> None:
        if self._rpc is not None:
            try:
                self._rpc.close()
            except Exception as e:
                print(f"Failed to close Discord RPC: {e}")
            finally:
                self._rpc = None
    
def presence_for(response, t):
    match response.screen:
        case Screens.MAIN_MENU | Screens.SLOTS | Screens.OPTIONS:
            return t("ui.presence.main_menu"), None
        case Screens.CREATION:
            return t("ui.presence.creation"), None
        case Screens.EXPLORATION:
            v = response.view
            room = t(f"zones.{v.zone_id}.rooms.{v.room_id}.name")
            level = t("ui.presence.level", level=v.player_summary.level)
            return t("ui.presence.exploring", room=room), level
        case _:
            return None