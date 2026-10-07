from dataclasses import dataclass
from enum import Enum, auto
from git import Repo
from pathlib import Path

import subprocess
import shutil

repo = Repo(Path(__file__).resolve(), search_parent_directories=True)
REPO_ROOT = Path(__file__).parent.parent.resolve()
DEPS_FILES = {"requirements.txt", "pyproject.toml"}

class UpdateState(Enum):
    UP_TO_DATE = auto()
    AVAILABLE = auto()
    UNAVAILABLE = auto()


@dataclass(frozen=True)
class UpdateStatus:
    state: UpdateState
    commit_diff: int = 0
    latest_commit: str | None = None

class UpdateError(Enum):
    DIRTY = auto()
    GIT_FAILED = auto()
    NOT_AVAILABLE = auto()

@dataclass(frozen=True)
class UpdateResult:
    success: bool
    error: UpdateError | None = None
    deps_changed: bool = False

def _git(*args: str, timeout: float = 10) -> subprocess.CompletedProcess[str] | None:
    if shutil.which("git") is None:
        return None
    try:
        return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.SubprocessError:
        return None

def check() -> UpdateStatus:
    fetch = _git("fetch", "--quiet", timeout=15)
    if fetch is None or fetch.returncode != 0:
        return UpdateStatus(state=UpdateState.UNAVAILABLE, commit_diff=0, latest_commit=None)
    
    count = _git("rev-list", "--count", "HEAD..@{u}")
    if count is None or count.returncode != 0:
        return UpdateStatus(state=UpdateState.UNAVAILABLE, commit_diff=0, latest_commit=None)
    
    behind = int(count.stdout.strip())
    if behind == 0:
        return UpdateStatus(state=UpdateState.UP_TO_DATE, commit_diff=0, latest_commit=None)
    
    last = _git("log", "-1", "--format=%h", "@{u}")
    latest = last.stdout.strip() if last is not None and last.returncode == 0 else None
    return UpdateStatus(state=UpdateState.AVAILABLE, commit_diff=behind, latest_commit=latest)

def apply(status: UpdateStatus) -> UpdateResult:
    if status.state is not UpdateState.AVAILABLE:
        return UpdateResult(success=False, error=UpdateError.NOT_AVAILABLE)

    dirty = _git("status", "--porcelain")
    if dirty is None or dirty.returncode != 0:
        return UpdateResult(success=False, error=UpdateError.GIT_FAILED)
    if dirty.stdout.strip():
        return UpdateResult(success=False, error=UpdateError.DIRTY)

    before = _git("rev-parse", "HEAD")
    if before is None or before.returncode != 0:
        return UpdateResult(success=False, error=UpdateError.GIT_FAILED)
    old_head = before.stdout.strip()

    pull = _git("pull", "--ff-only", timeout=60)
    if pull is None or pull.returncode != 0:
        return UpdateResult(success=False, error=UpdateError.GIT_FAILED)

    changed = _git("diff", "--name-only", old_head, "HEAD")
    files = set(changed.stdout.split()) if changed and changed.returncode == 0 else set()

    return UpdateResult(success=True, deps_changed=bool(files & DEPS_FILES))