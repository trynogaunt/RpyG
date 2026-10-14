"""Seul endroit où la version du jeu est définie.

pyproject.toml la lit via [tool.setuptools.dynamic], et l'interface l'injecte
dans la clé de traduction `ui.main_menu.version`.
"""

__version__ = "0.1.1"
