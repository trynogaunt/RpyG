import json
from pathlib import Path

import pytest

LANG_DIR = Path(__file__).resolve().parents[1] / "data" / "lang"
REFERENCE = "en"

def flat(d: dict, prefix: str = "") -> dict[str, str]:
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out |= flat(v, f"{prefix}{k}.")
        else:
            out[f"{prefix}{k}"] = v
    return out

def load(code: str) -> dict[str, str]:
    return flat(json.loads((LANG_DIR / f"{code}.json").read_text(encoding="utf-8")))

LOCALES = sorted(p.stem for p in LANG_DIR.glob("*.json") if p.stem != REFERENCE)

@pytest.mark.parametrize("code", LOCALES)
def test_same_keys_as_reference(code):
    ref, other = set(load(REFERENCE)), set(load(code))
    assert not ref - other, f"{code}: clés manquantes {sorted(ref - other)}"
    assert not other - ref, f"{code}: clés en trop {sorted(other - ref)}"


@pytest.mark.parametrize("code", LOCALES)
def test_same_placeholders_as_reference(code):
    import re
    ref, other = load(REFERENCE), load(code)
    for key in ref.keys() & other.keys():
        assert set(re.findall(r"{(\w+)}", ref[key])) == set(re.findall(r"{(\w+)}", other[key])), (
            f"{code}: marqueurs différents pour {key}"
        )