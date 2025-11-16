from ui.ui_controller import UIController
from  ui.screens.combat_screen import ennemy_group_label_names, build_combat_ui
import questionary


def test_health_bar(ui):
    bar = ui.health_bar(30, 100)
    assert "█" in bar
    assert "░" in bar

    full_bar = ui.health_bar(150, 150)
    assert "█" in full_bar
    assert "░" not in full_bar

    emmpty_bar = ui.health_bar(0, 100)
    assert "█" not in emmpty_bar
    assert "░" in emmpty_bar

def test_format_hp(ui):
    formatted = ui.format_hp(45, 100)
    assert formatted == "(45/100)"

    formatted_full = ui.format_hp(100, 100)
    assert formatted_full == "(100/100)"

    formatted_zero = ui.format_hp(0, 100)
    assert formatted_zero == "(0/100)"

def test_header(ui):
    header_lines = ui.header("Test Header")
    assert isinstance(header_lines, list)
    assert len(header_lines) == 3
    assert all(isinstance(line, str) for line in header_lines)

def test_message_box(ui):
    message = "This is a test message for the message box."
    box_lines = ui.message_box(message)
    assert isinstance(box_lines, list)
    assert len(box_lines) >= 3
    assert all(isinstance(line, str) for line in box_lines)

def test_text_block(ui):
    import io
    import sys

    captured_output = io.StringIO()
    sys.stdout = captured_output

    ui.text_block("This is a test paragraph to check text wrapping functionality in the UI controller.", wrap=True, indent=4)

    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    assert "This" in output

def test_ennemy_group_label_names():
    class MockEnemy:
        def __init__(self, name, kind=None):
            self.name = name
            self.kind = kind

    enemy1 = MockEnemy("Goblin", "goblin")
    enemy2 = MockEnemy("Goblin", "goblin")
    enemy3 = MockEnemy("Orc", "orc")

    assert ennemy_group_label_names([]) == "No enemies"
    assert ennemy_group_label_names([enemy1]) == "Goblin"
    assert ennemy_group_label_names([enemy1, enemy2]) == "Goblins (x2)"
    assert ennemy_group_label_names([enemy1, enemy3]) == "Enemies group"

def test_build_combat_ui():
    from classes.hero import Hero
    from classes.ennemy import Enemy
    from game.combat import Combat

    hero = Hero("Test Hero", 100, 10, 5)
    enemy1 = Enemy("Goblin", 30, 5, 2)
    enemy2 = Enemy("Orc", 50, 8, 3)

    combat = Combat(hero, [enemy1, enemy2])
    ui_lines = build_combat_ui(combat, actions=[])
    print(ui_lines)
    assert isinstance(ui_lines, list)
    assert any("Test " in line for line in ui_lines)
    assert any("Enemies" in line for line in ui_lines)

def test_status_section(ui):
    from classes.hero import Hero
    from classes.ennemy import Enemy
    from ui.screens.combat_screen import build_status_section

    hero = Hero("Test Hero", 100, 10, 5)
    enemy1 = Enemy("Goblin", 30, 5, 2)
    enemy2 = Enemy("Orc", 50, 8, 3)

    status_lines = build_status_section(ui, hero, [enemy1, enemy2])
  
    assert isinstance(status_lines, list)
    assert any("Test Hero" in line for line in status_lines)
    assert any("Goblin" in line for line in status_lines)
    assert any("Orc" in line for line in status_lines)

def test_build_combat_ui(ui):
    from classes.hero import Hero
    from classes.ennemy import Enemy
    from game.combat import Combat
    from ui.screens.combat_screen import build_combat_ui

    hero = Hero("Test Hero", 100, 10, 5)
    enemy1 = Enemy("Goblin", 30, 5, 2)
    enemy2 = Enemy("Orc", 50, 8, 3)

    combat = Combat(hero, [enemy1, enemy2])
    ui_lines = build_combat_ui(ui, combat)
    assert isinstance(ui_lines, list)
    assert any("Test Hero" in line for line in ui_lines)
    assert any("Enemies group" in line for line in ui_lines)

def test_render(ui):
    lines = [
        "Line 1: Test render function.",
        "Line 2: Another line.",
        "Line 3: Final line."
    ]
    import io
    import sys

    captured_output = io.StringIO()
    sys.stdout = captured_output

    ui.render(lines)

    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    for line in lines:
        assert line in output
    

def test_real_render(ui):
    from classes.hero import Hero
    from classes.ennemy import Enemy
    from game.combat import Combat
    from ui.screens.combat_screen import build_combat_ui
    combat = Combat(Hero("Hero", 100, 10, 5), [Enemy("Goblin", 30, 5, 2), Enemy("Orc", 50, 8, 3), Enemy("Troll", 80, 12,4), Enemy("Dragon", 200, 25,10), Enemy("Skeleton", 20, 4,1)])
    
    lines = []
    lines += ui.message_box("This is a test of the render function in the UIController class.")
    lines += build_combat_ui(ui, combat)
    import io
    import sys
    ui.render(lines)

if __name__ == "__main__":
    print("UIController tests running...")
    ui = UIController(width=70)
    print("Testing health bar...")
    test_health_bar(ui)
    print("Health bar tests passed.")
    print("Testing format HP...")
    test_format_hp(ui)
    print("Format HP tests passed.")
    print("Testing header...")
    test_header(ui)
    print("Header tests passed.")    
    print("Testing message box...")
    test_message_box(ui)
    print("Message box tests passed.")
    print("Testing text block...")
    test_text_block(ui)
    print("Text block tests passed.")
    print("Testing ennemy group label names...")
    test_ennemy_group_label_names()
    print("Ennemy group label names tests passed.")
    print("Testing build combat UI...")
    test_build_combat_ui(ui)
    print("Build combat UI tests passed.")
    print("Testing status section...")
    test_status_section(ui)
    print("Status section tests passed.")
    print("Testing render function...")
    test_render(ui)
    print("Render function tests passed.")
    print("All tests passed.")
    test_real_render(ui)
    choices = questionary.select(
        "Select an option to finish tests:",
        choices=["Exit"]
    ).ask()
