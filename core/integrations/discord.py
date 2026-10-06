import logging
import threading
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
        self._sent = None            
        self._pending = None         
        self._timer = None
        self._lock = threading.Lock()

    def connect(self) -> None:
        try:
            self._rpc = Presence(self._app_id)
            self._rpc.connect()
            log.info("Discord connecté")
        except Exception:
            log.exception("Discord indisponible")
            self._rpc = None

    def update(self, details, state=None) -> None:
        with self._lock:
            self._pending = (details, state)
        self._flush()

    def _flush(self) -> None:
        with self._lock:
            if self._rpc is None or self._pending is None:
                return
            if self._pending == self._sent:
                self._pending = None
                return
            wait = self.MIN_INTERVAL - (time.monotonic() - self._last)
            if wait > 0:
                if self._timer is None:        
                    self._timer = threading.Timer(wait, self._on_timer)
                    self._timer.daemon = True 
                    self._timer.start()
                return
            details, state = self._pending
            self._pending = None
            try:
                self._rpc.update(details=details, state=state, start=self._start)
                self._sent = (details, state)
                self._last = time.monotonic()
                log.info("Discord mis à jour : %s / %s", details, state)
            except Exception:
                log.exception("Échec de la mise à jour Discord")
                self._rpc = None

    def _on_timer(self) -> None:
        with self._lock:
            self._timer = None
        self._flush()

    def close(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            rpc, self._rpc = self._rpc, None
        if rpc is not None:
            try:
                rpc.close()
            except Exception:
                pass
        log.info("Discord fermé")