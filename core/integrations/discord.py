import logging
import time
from pypresence import Presence

log = logging.getLogger(__name__)

class DiscordIntegration:
    MIN_INTERVAL = 15

    def __init__(self, app_id):
        self.app_id = app_id
        self._rpc = None
        self._start = int(time.time())
        self._last = float("-inf")
        self._pending = None

    def connect(self):
        try:
            self._rpc = Presence(self.app_id)
            self._rpc.connect()
            log.info("Discord RPC connecté")
        except Exception as e:
            log.exception("Échec de connexion à Discord RPC")
            print("PRESENCE FAILED: ", e)
            self._rpc = None
        
        print("PRESENCE CONNECTED")

    def update(self, details: str, state: str = None) -> None:
        if self._rpc is None:
            return
        self._pending = (details, state)
        self.flush()

    def flush(self) -> None:
        """Envoie l'état en attente si le délai minimum est écoulé."""
        if self._rpc is None or self._pending is None:
            return
        if time.monotonic() - self._last < self.MIN_INTERVAL:
            return
        details, state = self._pending
        try:
            self._rpc.update(details=details, state=state, start=self._start, large_image="large_image_key")
            self._last = time.monotonic()
            self._pending = None
            log.info("Présence mise à jour : %s / %s", details, state)
        except Exception:
            log.exception("Échec de mise à jour de la présence")
            self._rpc = None

    def close(self) -> None:
        if self._rpc is not None:
            try:
                self._rpc.close()
            except Exception:
                log.exception("Échec de fermeture de Discord RPC")
            finally:
                self._rpc = None