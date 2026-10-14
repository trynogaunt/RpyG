import threading
from pathlib import Path

import pytest

from core import boot as boot_module
from core.boot import Boot, StepStatus
from core.updater import UpdateState, UpdateStatus

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
UP_TO_DATE = UpdateStatus(state=UpdateState.UP_TO_DATE, commit_diff=0, latest_commit=None)


class Settings:
    discord_integration = False


@pytest.fixture(autouse=True)
def fast_updates(monkeypatch):
    """Par défaut, la recherche de mises à jour répond tout de suite, sans réseau."""
    monkeypatch.setattr(boot_module, "check", lambda: UP_TO_DATE)


def run(boot) -> list[tuple[str, StepStatus]]:
    events = []
    boot.run(lambda i, step, status: events.append((step.key, status)))
    return events


def finished(events) -> dict[str, StepStatus]:
    return {key: status for key, status in events if status is not StepStatus.RUNNING}


def test_steps_without_discord():
    assert [s.key for s in Boot(Settings(), DATA_DIR).steps()] == ["items", "world", "updates"]


def test_discord_step_only_when_enabled():
    settings = Settings()
    settings.discord_integration = True
    assert "discord" in [s.key for s in Boot(settings, DATA_DIR).steps()]


def test_each_step_reports_running_then_result():
    events = run(Boot(Settings(), DATA_DIR))
    assert events == [
        ("items", StepStatus.RUNNING), ("items", StepStatus.DONE),
        ("world", StepStatus.RUNNING), ("world", StepStatus.DONE),
        ("updates", StepStatus.RUNNING), ("updates", StepStatus.DONE),
    ]


def test_build_game_uses_loaded_data():
    boot = Boot(Settings(), DATA_DIR)
    run(boot)
    game = boot.build_game()
    assert "wooden_sword" in game.catalog
    assert game.world is boot.world
    assert game.update == UP_TO_DATE


def test_failed_update_check_is_unavailable(monkeypatch):
    monkeypatch.setattr(boot_module, "check", lambda: None)
    assert finished(run(Boot(Settings(), DATA_DIR)))["updates"] is StepStatus.UNAVAILABLE


def test_slow_update_check_times_out_and_reaches_the_game_later(monkeypatch):
    release = threading.Event()
    def slow_check():
        release.wait(5)
        return UP_TO_DATE
    monkeypatch.setattr(boot_module, "check", slow_check)
    monkeypatch.setattr(boot_module, "UPDATE_TIMEOUT", 0.05)

    boot = Boot(Settings(), DATA_DIR)
    assert finished(run(boot))["updates"] is StepStatus.TIMEOUT
    game = boot.build_game()
    assert game.update is None

    release.set()
    for _ in range(100):
        if game.update is not None:
            break
        threading.Event().wait(0.01)
    assert game.update == UP_TO_DATE


def test_unreachable_discord_is_unavailable_but_kept_for_reconnection(monkeypatch):
    from core.integrations import discord
    monkeypatch.setattr(discord.DiscordIntegration, "connect", lambda self: None)   # _rpc reste None
    monkeypatch.setattr(discord.DiscordIntegration, "start_heartbeat", lambda self: None)
    settings = Settings()
    settings.discord_integration = True
    boot = Boot(settings, DATA_DIR)
    assert finished(run(boot))["discord"] is StepStatus.UNAVAILABLE
    assert boot.presence is not None and not boot.presence.connected


def test_mandatory_step_failure_propagates(monkeypatch):
    def broken():
        raise RuntimeError("monde corrompu")
    monkeypatch.setattr(boot_module, "load_world", lambda data_dir: broken())
    with pytest.raises(RuntimeError):
        run(Boot(Settings(), DATA_DIR))


def test_step_delay_pauses_after_each_step(monkeypatch):
    pauses = []
    monkeypatch.setattr(boot_module.time, "sleep", pauses.append)
    run(Boot(Settings(), DATA_DIR, step_delay=0.7))
    assert pauses == [0.7, 0.7, 0.7]


def test_no_pause_by_default(monkeypatch):
    pauses = []
    monkeypatch.setattr(boot_module.time, "sleep", pauses.append)
    run(Boot(Settings(), DATA_DIR))
    assert pauses == []
