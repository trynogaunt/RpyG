from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.game.actions import Back, SetLocale


class OptionsScreen(BaseConsoleScreen):
    def draw(self):
        v = self.view
        self.rule()
        self.centered(self.t("ui.options.title"))
        self.rule()
        print()
        current = self.t(f"ui.options.language_name.{v.locale}")
        print(f"{self.t('ui.options.language')} : {current}")
        print()

    def ask(self):
        v = self.view
        options = []
        for code in v.available_locales:
            marker = ">" if code == v.locale else " "
            name = self.t(f"ui.options.language_name.{code}")
            options.append((f"{marker} {name}", SetLocale(locale=code)))
        options.append((self.t("ui.common.back"), Back()))
        return self.choose(options)