import json
import re
from pathlib import Path

import pytest

from core.version import __version__

LANG_DIR = Path(__file__).resolve().parents[1] / "data" / "lang"


def test_version_is_semver():
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)


@pytest.mark.parametrize("lang_file", sorted(LANG_DIR.glob("*.json")), ids=lambda p: p.stem)
def test_locales_do_not_hardcode_the_version(lang_file):
    text = json.loads(lang_file.read_text(encoding="utf-8"))["ui"]["main_menu"]["version"]
    assert "{version}" in text
    assert not re.search(r"\d+\.\d+", text), "la version doit venir de core/version.py"
