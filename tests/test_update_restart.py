import sys
from pathlib import Path

import pytest

import main
from core.enums import Screens
from core.game import game as game_module
from core.game.actions import ApplyUpdate
from core.updater import UpdateError, UpdateResult, UpdateState, UpdateStatus

AVAILABLE = UpdateStatus(UpdateState.AVAILABLE, commit_diff=2, latest_commit="abc123")


@pytest.fixture
def menu(game):
    game.update = AVAILABLE
    return game


def apply_returns(monkeypatch, result: UpdateResult):
    monkeypatch.setattr(game_module, "apply", lambda status: result)


def test_successful_update_quits_and_asks_for_restart(menu, monkeypatch):
    apply_returns(monkeypatch, UpdateResult(success=True))
    response = menu.handle_action(ApplyUpdate())
    assert response.screen is Screens.EXIT
    assert menu.restart_requested


def test_update_with_new_dependencies_does_not_restart(menu, monkeypatch):
    apply_returns(monkeypatch, UpdateResult(success=True, deps_changed=True))
    response = menu.handle_action(ApplyUpdate())
    assert response.screen is Screens.MAIN_MENU
    assert not menu.restart_requested
    assert [m.key for m in response.messages] == ["ui.update.success", "ui.update.deps_changed", "ui.update.restart"]
    assert menu.update.state is UpdateState.UP_TO_DATE


def test_failed_update_stays_on_menu(menu, monkeypatch):
    apply_returns(monkeypatch, UpdateResult(success=False, error=UpdateError.DIRTY))
    response = menu.handle_action(ApplyUpdate())
    assert response.screen is Screens.MAIN_MENU
    assert not menu.restart_requested
    assert [m.key for m in response.messages] == ["ui.update.error.dirty"]


def test_restart_relaunches_main_py_with_same_options(monkeypatch):
    calls = []
    monkeypatch.setattr(main.subprocess, "call", lambda cmd: calls.append(cmd) or 0)
    monkeypatch.setattr(sys, "argv", ["rpyg", "--ui", "console"])
    with pytest.raises(SystemExit) as exit_info:
        main.restart()
    assert calls == [[sys.executable, str(Path(main.__file__).resolve()), "--ui", "console"]]
    assert exit_info.value.code == 0


def test_restart_propagates_child_exit_code(monkeypatch):
    monkeypatch.setattr(main.subprocess, "call", lambda cmd: 3)
    monkeypatch.setattr(sys, "argv", ["main.py"])
    with pytest.raises(SystemExit) as exit_info:
        main.restart()
    assert exit_info.value.code == 3
