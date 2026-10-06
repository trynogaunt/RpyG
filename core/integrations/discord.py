from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass

from pypresence import Presence

try: 
    from pypresence import StatusDisplayType
except ImportError: 
    StatusDisplayType = None

from core.enums import Screens

log = logging.getLogger(__name__)

DISCORD_APP_ID = "1439725986290860132"

LARGE_IMAGE_DEFAULT = "logo"
SMALL_IMAGE = "logo"
SMALL_TEXT = "RPyG"
LARGE_TEXT = "RPyG"
SCREEN_IMAGES: dict[Screens, str] = {
    # Screens.CREATION: "creation",
}

ZONE_IMAGES: dict[str, str] = {
    # zone_id -> nom de l'asset dans le portail
    "entry_village": "zone_entry_village",
    "flooded_cave": "zone_flooded_cave",
}

DEFAULT_BUTTONS = (
    {"label": "GitHub", "url": "https://github.com/trynogaunt/RPyG"},
)


@dataclass(frozen=True)
class PresenceInfo:
    details: str
    state: str | None = None
    large_text: str | None = None
    large_image: str | None = None
    small_image: str | None = None
    small_text: str | None = None


def presence_for(response, t) -> PresenceInfo | None:
    match response.screen:
        case Screens.MAIN_MENU | Screens.SLOTS | Screens.OPTIONS:
            return PresenceInfo(t("ui.presence.main_menu"), large_image=SCREEN_IMAGES.get(response.screen))
        case Screens.CREATION:
            return PresenceInfo(t("ui.presence.creation"), large_image=SCREEN_IMAGES.get(response.screen)   )
        case Screens.EXPLORATION:
            v = response.view
            room = t(f"zones.{v.zone_id}.rooms.{v.room_id}.name")
            return PresenceInfo(
                details=t("ui.presence.exploring", room=room),
                state=t("ui.presence.level", level=v.player_summary.level),
                large_image=ZONE_IMAGES.get(v.zone_id),
                large_text=t(f"zones.{v.zone_id}.rooms.{v.room_id}.name"),
                small_text=SMALL_TEXT,
            )
        case _:
            return None


class DiscordIntegration:
    MIN_INTERVAL = 15

    def __init__(
        self,
        app_id: str = DISCORD_APP_ID,
        *,
        large_image: str | None = LARGE_IMAGE_DEFAULT,
        large_text: str | None = LARGE_TEXT,
        small_image: str | None = SMALL_IMAGE,
        small_text: str | None = None,
        buttons: tuple[dict, ...] = DEFAULT_BUTTONS,
    ):
        self._app_id = app_id
        self._large_image = large_image
        self._large_text = large_text
        self._small_image = small_image
        self._small_text = small_text
        self._buttons = list(buttons)[:2]

        self._rpc: Presence | None = None
        self._start = int(time.time())
        self._last = float("-inf")
        self._sent: PresenceInfo | None = None     
        self._pending: PresenceInfo | None = None 
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def connect(self) -> None:
        try:
            self._rpc = Presence(self._app_id)
            self._rpc.connect()
            log.info("Discord connected")
        except Exception:
            log.exception("Discord unavailable")
            self._rpc = None

    def close(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            rpc, self._rpc = self._rpc, None
            self._pending = None
        if rpc is not None:
            try:
                rpc.clear(pid=os.getpid())
            except Exception:
                pass
            try:
                rpc.close()
            except Exception:
                pass

    def update(self, info: PresenceInfo | None) -> None:
        if info is None:
            return
        with self._lock:
            self._pending = info
        self._flush()

    def _kwargs(self, info: PresenceInfo) -> dict:
        kwargs = {
            "pid": os.getpid(),        
            "details": info.details,
            "state": info.state,
            "start": self._start,
            "large_image": info.large_image or self._large_image,
            "large_text": info.large_text or self._large_text,
            "small_image": info.small_image or self._small_image,
            "small_text": info.small_text or self._small_text,
            "buttons": self._buttons or None,
        }
        if StatusDisplayType is not None:
            kwargs["status_display_type"] = StatusDisplayType.DETAILS

        return {k: v for k, v in kwargs.items() if v is not None}

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

            info, self._pending = self._pending, None
            try:
                self._rpc.update(**self._kwargs(info))
                self._sent = info
                self._last = time.monotonic()
                log.info("Discord updated: %s / %s", info.details, info.state)
            except Exception:
                log.exception("Failed to update Discord")
                self._rpc = None

    def _on_timer(self) -> None:
        with self._lock:
            self._timer = None
        self._flush()