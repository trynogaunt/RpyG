def test_hero_initialization():
    from models.hero import Hero
    hero = Hero(name="TestHero", health=100, strength=50, luck=20, speed=30, gold=0)
    assert hero.name == "TestHero"
    assert hero.health == 100
    assert hero.strength == 50
    assert hero.luck == 20
    assert hero.speed == 30
    assert hero.current_room is None
    assert hero.current_zone is None
    assert hero.visited_rooms == set()
    assert hero.active_effects == []
    assert hero.gold == 0

if __name__ == "__main__":
    test_hero_initialization()
    print("All tests passed.")