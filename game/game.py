class Game:
    def __init__(self, ui: "UIController", hero: Hero):
        self.ui = ui
        self.hero = hero
        self.was_loaded = False

    def run(self):
        if self.was_loaded:
            self.ui.text_block(f"Welcome back, {self.hero.name}! Resuming your adventure...", wrap=True)
        else:
            self.ui.text_block(f"Welcome, {self.hero.name}! Your adventure begins now...", wrap=True)
        while self.hero.is_alive():
            self.ui.empty_line()
            self.ui.text_block("Game loop would proceed here...", wrap=True)
            break
    
    def load(self, save_file: str):
        self.was_loaded = True
        pass