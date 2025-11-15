from classes import hero, room
import combat

def get_actions(player: hero.Hero) -> list:
    room = player.current_room
    actions = []

    if room.exits:
        actions.append("move")

    if room.enemies:
        actions.append("attack")
    
    actions.append("inspect")
    actions.append("inventory")
    actions.append("exit")

    return actions

def apply_action(player, action, parameter=None):
    room = player.current_room
    if action == "move":
        from ui_console import show_room, ask_direction 
        direction = parameter
        while True:
            moved = player.move(direction)
            if moved:
                break
            show_room(player, "No exit in that direction.")
            direction = ask_direction(room)
            if direction is None:
                break

    elif action == "attack":
        if room.enemies:
            enemy = room.enemies[0]  # Engage the first enemy in the room
            combat.run_combat(player, enemy)
            if not enemy.is_alive():
                room.enemies.remove(enemy)
    elif action == "inspect":
        pass
    elif action == "inventory":
        from ui_console import show_inventory
        show_inventory(player)
    elif action == "exit":
        print("Exiting the game. Thanks for playing!")
        exit()
