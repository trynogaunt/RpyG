# Python RPG Game

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-WIP-orange)
![Last Commit](https://img.shields.io/github/last-commit/trynogaunt/RpyG)
![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)


## Table of Contents
- Description
- Installation
- Features
- Project Structure
- Roadmap
- Contribution
- License
- Author

---

## Description

A text-based RPG game made in Python with a console UI.  
The player creates a hero and explores a world made of interconnected rooms.

🎯 Current goal: build a **solid foundation** for an extensible RPG  
(exploration, combat, quests, equipment, saving).

Already implemented:

- Interactive main menu
- Character creation with stat allocation
- Styled console UI through a custom renderer
- Structured game loop using a state machine
- First playable room with basic exploration actions

---

## Installation

Clone the repository:

    git clone https://github.com/trynogaunt/RpyG
    cd RpyG

Run the game:

    python app.py

> ⚠️ Requires Python **3.10+** (usage of match/case syntax)

---

## Features

### ✔ Implemented

| System | Details |
|--------|---------|
| Character Creation | Name + stat distribution (Health, Strength, Speed, Luck) |
| Console UI | Styled rendering + interactive menus |
| Game Loop | States: Exploration / Menu / Pause / Future Combat / Exit |
| World System | Starting room + contextual actions |
| Modular Architecture | Split into Game / World / UI / Character classes |

---

### 🔜 In development

- Room-to-room navigation (N, S, E, W)
- Context-aware actions based on current room
- (Re)implementation of the combat system
- Inventory + equipment
- Save / Load system

---

## Project Structure

    RpyG/
    ├── app.py                      # Game entry point (menu + launch Game)
    ├── game/
    │   ├── game.py                 # Game class + main loop (state machine)
    │   └── creation_flow.py        # Character creation process
    ├── world/
    │   ├── room.py                 # Room class
    │   ├── world.py                # World container
    │   └── build_world.py          # First playable map
    ├── classes/
    │   ├── character.py            # Base character class
    │   ├── hero.py                 # Hero (stats + state + room position)
    │   ├── enemy.py                # Enemy class (work-in-progress)
    │   └── interface_class.py      # CharacterCreationState class
    ├── ui/
    │   ├── ui_controller.py        # Console renderer
    │   └── screens/                # Menus & creation screens
    └── README.md

> Legacy inventory/enemy systems are currently being refactored.

---

## Roadmap

### 🧱 Phase 1 — Exploration (current)
- [x] Character creation
- [x] Game loop with state machine
- [x] Starting room spawn
- [ ] Movement between rooms (N/S/E/W)
- [ ] Random encounters on movement

### ⚔️ Phase 2 — Combat & Equipment
- [ ] Turn-based combat
- [ ] Damage calculation based on stats (Strength/Luck)
- [ ] Equipment + inventory
- [ ] Simple loot

### 💾 Phase 3 — Persistence & QoL
- [ ] Save / Load system
- [ ] Action / event log
- [ ] Unit tests

### 🔮 Future ideas
- Procedural dungeon generation
- Quest / NPC system
- Skills and talent trees
- Optional rogue-lite mode

---

## Contribution

Contributions are welcome 🎯

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Open a Pull Request 🚀

---

## License

Licensed under MIT — see `LICENSE` for details.

---

## Author

Made with ❤️ in Python  
by **Trynogaunt**
