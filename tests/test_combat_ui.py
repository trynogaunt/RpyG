from ui.ui_controller import UIController

def test_health_bar():
    ui = UIController(width=40)
    bar = ui.health_bar(30, 100)
    assert "█" in bar
    assert "░" in bar

    full_bar = ui.health_bar(150, 150)
    assert "█" in full_bar
    assert "░" not in full_bar

    emmpty_bar = ui.health_bar(0, 100)
    assert "█" not in emmpty_bar
    assert "░" in emmpty_bar

if __name__ == "__main__":
    test_health_bar()