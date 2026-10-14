from pathlib import Path
from core.game.I18n import Translation
from core.game.settings import Settings, default_settings_path
from core.boot import Boot
import argparse
import importlib
import logging
import subprocess
import sys

log = logging.getLogger(__name__)
logging.basicConfig(filename="rpyg.log", level=logging.INFO)

FRONTENDS = {
    "textual": "core.ui.textual",
    "console": "core.ui.console"
}

FALLBACK = "console"

def parse_args():
    parser = argparse.ArgumentParser(prog="rpyg")
    parser.add_argument("--ui", choices=FRONTENDS.keys())
    parser.add_argument("--loading-delay", type=float, default=0.0, metavar="SECONDES",
                        help="pause après chaque étape de l'écran de chargement (pour les captures d'écran)")
    return parser.parse_args()

def resolve_frontend(cli_choice, settings):
    candidates = [cli_choice, settings.interface, FALLBACK]
    for name in candidates:
        if name not in FRONTENDS:
            continue
        try:
            return importlib.import_module(FRONTENDS[name])
        except ImportError as e:
            raise ImportError(f"Failed to import frontend '{name}'") from e
    raise ImportError("No suitable frontend found.")

def main():
    data_dir = Path(__file__).parent / "data"
    lang_dir = data_dir / "lang"
    args = parse_args()

    settings = Settings.load(default_settings_path())

    available = {p.stem for p in lang_dir.glob("*.json")}
    if settings.locale not in available:
        settings.locale = "en"

    translation = Translation(locales_dir=lang_dir, locales=settings.locale)
    
    frontend = resolve_frontend(args.ui, settings)
    boot = Boot(settings=settings, data_dir=data_dir, step_delay=args.loading_delay)
    frontend.run(boot, translation=translation, settings=settings)

    if boot.game is not None and boot.game.restart_requested:
        print(translation.t("ui.update.restarting"), flush=True)
        restart()


def restart() -> None:
    """Relance le jeu avec les mêmes options, pour charger le code tout juste mis à jour.

    Un nouveau processus plutôt que os.execv : sous Windows, execv rend la main au terminal
    pendant que le jeu tourne encore, et les saisies se mélangent.
    """
    log.info("Redémarrage après mise à jour")
    sys.exit(subprocess.call([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]))


if __name__ == "__main__":
    main()