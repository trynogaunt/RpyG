from pathlib import Path

import pytest

import core.items  # noqa: F401  (l'import enregistre les types et les effets)
from core.game.I18n import Translation
from core.items.base import Item, get_item_type

# ADAPTE : dossier des locales (dans main.py : data_dir / "lang")
LANG_DIR = Path(__file__).resolve().parents[1] / "data" / "lang"
LOCALES = ["en", "fr", "de", "es"]

WOODEN_SWORD = {
    "id": "wooden_sword",
    "type": "weapon",
    "max_stack": 1,
    "params": {"damage": 1},
}


def make_item(**overrides) -> Item:
    return Item(**{**WOODEN_SWORD, **overrides})


# ---------- Le type "weapon" ----------

def test_weapon_type_is_registered():
    assert get_item_type("weapon").name == "weapon"


def test_weapon_type_capabilities():
    weapon = get_item_type("weapon")
    assert weapon.equippable is True
    assert weapon.usable is False
    assert weapon.stackable is False


# ---------- Les données de l'épée ----------

def test_wooden_sword_is_built_from_its_data():
    sword = make_item()
    assert sword.id == "wooden_sword"
    assert sword.type == "weapon"
    assert sword.params["damage"] == 1
    assert sword.effect is None


def test_wooden_sword_passes_weapon_validation():
    get_item_type("weapon").validate(make_item())   # ne doit pas lever


def test_wooden_sword_max_stack_matches_non_stackable_type():
    # Un type non empilable impose max_stack == 1 (règle que le loader appliquera).
    assert get_item_type(make_item().type).stackable is False
    assert make_item().max_stack == 1


# ---------- Validation : données invalides ----------

@pytest.mark.parametrize(
    "params",
    [{}, {"damage": 0}, {"damage": -2}, {"damage": "3"}, {"damage": 1.5},
     {"damage": True}, {"damage": None}],
)
def test_weapon_with_invalid_damage_is_rejected(params):
    with pytest.raises(ValueError, match="wooden_sword"):
        get_item_type("weapon").validate(make_item(params=params))


def test_weapon_with_use_effect_is_rejected():
    with pytest.raises(ValueError, match="wooden_sword"):
        get_item_type("weapon").validate(make_item(effect="heal"))


# ---------- Traductions ----------

@pytest.mark.parametrize("locale", LOCALES)
@pytest.mark.parametrize("field", ["name", "description"])
def test_wooden_sword_is_translated_in_every_locale(locale, field):
    key = f"items.wooden_sword.{field}"
    translations = Translation(locales_dir=LANG_DIR, locales=locale).translations
    assert key in translations
    
def test_wooden_sword_english_texts():
    t = Translation(locales_dir=LANG_DIR, locales="en")
    assert t.t("items.wooden_sword.name") == "Wooden Sword"
    assert t.t("items.wooden_sword.description") == (
        "A basic wooden sword, suitable for beginners."
    )