import logging
import time
from pypresence import Presence

log = logging.getLogger(__name__)

class DiscordIntegration:
    MIN_INTERVAL = 15
    
    def __init__(self, app_id: str):
        self._app_id = app_id
        self._rpc = None
        self._start = int(time.time())
        self._last = float("-inf")

    def connect(self) -> None:
        print("PRESENCE connect appelé")
        try:
            self._rpc = Presence(self._app_id)
            self._rpc.connect()
            print("PRESENCE connecté")
        except Exception as e:
            print("PRESENCE connect échoué :", repr(e))
            self._rpc = None

    def update(self, details, state=None) -> None:
        print("PRESENCE update :", details, state, "rpc =", self._rpc)
        if self._rpc is None:
            print("PRESENCE -> abandon : pas connecté")
            return
        if time.monotonic() - self._last < self.MIN_INTERVAL:
            print("PRESENCE -> abandon : limite de fréquence")
            return
        try:
            self._rpc.update(details=details, state=state, start=self._start)
            self._last = time.monotonic()
            print("PRESENCE -> envoyé")
        except Exception as e:
            print("PRESENCE update échoué :", repr(e))
            self._rpc = None