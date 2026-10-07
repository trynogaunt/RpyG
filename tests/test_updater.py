import shutil
import subprocess
from pathlib import Path

import pytest

from core import updater  # adapte l'import à ton arborescence
from core.updater import UpdateError, UpdateState, UpdateStatus

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git requis")


def git(*args: str, cwd: Path) -> None:
    subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", *args],
        cwd=cwd, check=True, capture_output=True, text=True,
    )


def commit(repo: Path, name: str, content: str | None = None) -> None:
    (repo / name).write_text(content if content is not None else name)
    git("add", name, cwd=repo)
    git("commit", "-m", f"add {name}", cwd=repo)


@pytest.fixture
def repos(tmp_path, monkeypatch):
    """origin (bare) + dev (qui pousse) + player (le jeu, qui vérifie)."""
    origin = tmp_path / "origin.git"
    dev = tmp_path / "dev"
    player = tmp_path / "player"

    git("init", "--bare", "-b", "main", str(origin), cwd=tmp_path)
    git("init", "-b", "main", str(dev), cwd=tmp_path)
    git("remote", "add", "origin", str(origin), cwd=dev)
    commit(dev, "first.txt")
    git("push", "-u", "origin", "main", cwd=dev)
    git("clone", str(origin), str(player), cwd=tmp_path)

    monkeypatch.setattr(updater, "REPO_ROOT", player)
    return dev, player


# ---------- check() ----------

def test_up_to_date(repos):
    status = updater.check()
    assert status.state is UpdateState.UP_TO_DATE
    assert status.commit_diff == 0


def test_available_after_push(repos):
    dev, _ = repos
    commit(dev, "second.txt")
    commit(dev, "third.txt")
    git("push", cwd=dev)

    status = updater.check()
    assert status.state is UpdateState.AVAILABLE
    assert status.commit_diff == 2
    assert status.latest_commit  # hash court non vide


def test_local_changes_are_not_an_update(repos):
    """Un fichier modifié localement n'est pas une mise à jour disponible."""
    _, player = repos
    (player / "first.txt").write_text("modifié")

    assert updater.check().state is UpdateState.UP_TO_DATE


def test_unavailable_outside_a_repo(tmp_path, monkeypatch):
    monkeypatch.setattr(updater, "REPO_ROOT", tmp_path)
    assert updater.check().state is UpdateState.UNAVAILABLE


def test_unavailable_without_git(repos, monkeypatch):
    monkeypatch.setattr(updater.shutil, "which", lambda _: None)
    assert updater.check().state is UpdateState.UNAVAILABLE


def test_unavailable_when_origin_unreachable(repos):
    _, player = repos
    git("remote", "set-url", "origin", str(player / "inexistant"), cwd=player)
    assert updater.check().state is UpdateState.UNAVAILABLE


# ---------- apply() ----------

def push_new_commit(dev: Path, name: str = "second.txt", content: str | None = None):
    commit(dev, name, content)
    git("push", cwd=dev)


def test_apply_pulls_new_commits(repos):
    dev, player = repos
    push_new_commit(dev)

    result = updater.apply(updater.check())

    assert result.success is True
    assert result.error is None
    assert result.deps_changed is False
    assert (player / "second.txt").exists()
    assert updater.check().state is UpdateState.UP_TO_DATE


def test_apply_flags_dependency_change(repos):
    dev, _ = repos
    push_new_commit(dev, "requirements.txt", "textual\n")

    result = updater.apply(updater.check())

    assert result.success is True
    assert result.deps_changed is True


def test_apply_refuses_dirty_repo(repos):
    dev, player = repos
    push_new_commit(dev)
    (player / "first.txt").write_text("modifié")

    result = updater.apply(updater.check())

    assert result.success is False
    assert result.error is UpdateError.DIRTY
    assert not (player / "second.txt").exists()   # rien n'a été tiré


def test_apply_refuses_when_not_available(repos):
    result = updater.apply(updater.check())   # déjà à jour

    assert result.success is False
    assert result.error is UpdateError.NOT_AVAILABLE


def test_apply_refuses_unavailable_status(repos):
    result = updater.apply(UpdateStatus(UpdateState.UNAVAILABLE))

    assert result.error is UpdateError.NOT_AVAILABLE


def test_apply_fails_on_diverged_history(repos):
    """Commit local + commit distant : --ff-only refuse, rien n'est écrasé."""
    dev, player = repos
    commit(player, "local.txt")
    push_new_commit(dev)

    result = updater.apply(updater.check())

    assert result.success is False
    assert result.error is UpdateError.GIT_FAILED
    assert (player / "local.txt").exists()
    assert not (player / "second.txt").exists()