
from pathlib import Path
from core.game.I18n import Translation
tr = Translation(locales='fr', locales_dir=Path('data/lang'))   # mêmes arguments que dans main.py
print(len(tr.translations))
print(tr.t('ui.bindings.explore'))
print(tr.t('ui.bindings.quit'))