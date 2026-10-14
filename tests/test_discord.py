import pytest

from core.integrations import discord
from core.integrations.discord import DiscordIntegration, PresenceInfo


class FakePresence:
    """Simule pypresence : `discord_running` décide si Discord répond."""
    discord_running = True
    sent: list[dict] = []

    def __init__(self, app_id):
        pass

    def connect(self):
        if not FakePresence.discord_running:
            raise ConnectionRefusedError("Discord fermé")

    def update(self, **kwargs):
        if not FakePresence.discord_running:
            raise BrokenPipeError("Discord fermé")
        FakePresence.sent.append(kwargs)

    def clear(self, pid=None): ...
    def close(self): ...


@pytest.fixture
def presence(monkeypatch):
    FakePresence.discord_running = True
    FakePresence.sent = []
    monkeypatch.setattr(discord, "Presence", FakePresence)
    monkeypatch.setattr(DiscordIntegration, "start_heartbeat", lambda self: None)   # battements déclenchés à la main
    p = DiscordIntegration()
    p.MIN_INTERVAL = 0
    p.connect()
    yield p
    p.close()


INFO = PresenceInfo(details="Exploration de la Place")


def test_connected_after_connect(presence):
    assert presence.connected


def test_unreachable_discord_is_disconnected(monkeypatch):
    FakePresence.discord_running = False
    monkeypatch.setattr(discord, "Presence", FakePresence)
    p = DiscordIntegration()
    p.connect()
    assert not p.connected


def test_heartbeat_detects_discord_closed(presence):
    presence.update(INFO)
    FakePresence.discord_running = False
    presence._on_heartbeat()
    assert not presence.connected


def test_heartbeat_reconnects_and_republishes_presence(presence):
    presence.update(INFO)
    FakePresence.discord_running = False
    presence._on_heartbeat()
    FakePresence.sent.clear()

    FakePresence.discord_running = True
    presence._on_heartbeat()
    assert presence.connected
    assert [s["details"] for s in FakePresence.sent] == ["Exploration de la Place"]


def test_update_while_disconnected_is_sent_after_reconnection(presence):
    FakePresence.discord_running = False
    presence._on_heartbeat()                      # rien à envoyer, mais la reconnexion échoue
    presence.update(PresenceInfo(details="Menu"))
    assert FakePresence.sent == []

    FakePresence.discord_running = True
    presence._on_heartbeat()
    assert [s["details"] for s in FakePresence.sent] == ["Menu"]


def test_close_stops_heartbeat(monkeypatch):
    monkeypatch.setattr(discord, "Presence", FakePresence)
    p = DiscordIntegration()
    p.HEARTBEAT = 60
    p.start_heartbeat()
    assert p._heartbeat is not None
    p.close()
    assert p._heartbeat is None
    p.start_heartbeat()                           # un battement en cours ne relance rien après close()
    assert p._heartbeat is None
