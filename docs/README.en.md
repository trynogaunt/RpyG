# Python RPG Game

[![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Features](#features)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Technologies](#technologies)
- [Roadmap](#roadmap)
- [Contribution](#contribution)
- [License](#license)
- [Author](#author)

## Description

An RPG (Role-Playing Game) developed in Python with a combat system, inventory management, and character progression.

This project is a text-based RPG game where the player embodies a hero who can:
- Fight enemies
- Manage inventory of weapons, armor, and consumables
- Progress in level and improve statistics
- Equip different types of items

## Installation

1. Clone this repository:
```bash
git clone <https://github.com/trynogaunt/RpyG>
cd "RpyG"
```

2. Make sure you have Python 3.7+ installed:
```bash
python --version
```

3. Launch the game:
```bash
python app.py
```

## Features

### Base Classes
- **Hero**: Player character with statistics (health, strength, defense)
- **Enemy**: Enemies with combat AI
- **Item System**: Complete object system
  - Weapons (variable damage according to strength)
  - Armor (protection)
  - Consumables (healing potions, etc.)

### Combat System
- Turn-based combat
- Damage calculation based on statistics
- Dodge and critical hit system

### Inventory
- Item management
- Equipment of weapons and armor
- Use of consumables

## Project Structure

```
RPyG/
├── classes/
│   ├── hero.py          # Hero Class
│   ├── enemy.py         # Enemy Class  
│   ├── Item.py          # Object System
│   └── inventory.py     # Inventory Management
├── main.py              # Game entry point
├── README.md
└── .gitignore
```

## Usage

```python
# Example of creating a hero
from classes.hero import Hero
from classes.Item import Weapon

hero = Hero("Adventurer", 100, 20, 10)
sword = Weapon("Steel Sword", "A sharp sword", 15, 0.1)
hero.attack(enemy)
```

## Technologies

- **Python 3.7+**
- Object-Oriented Programming (OOP)
- Modular architecture with separate classes

## Roadmap

### Current — Playable Prototype
- [x] Basic character creation
- [] Weapon & armor system
- [x] Turn-based combat
- [] Minimal inventory

### Next Steps — Combat Enhancements
- [ ] Dodge system based on Speed
- [ ] Critical hit system based on Luck
- [x] Two-handed weapon handling
- [ ] Improved battle UI (interactive menus)

### Loot & Progression
- [ ] Enemy variety + random loot system
- [ ] Level progression & skill upgrades
- [ ] Equipment upgrades

### Quality of Life
- [ ] Save / Load system
- [x] Combat log
- [ ] Unit testing

### Future ideas
- [ ] Magic skills
- [ ] Zone exploration
- [ ] Narrative events
- [ ] Rogue-lite mode (optional)

## Contribution

Contributions are welcome! Feel free to:
1. Fork the project
2. Create a branch for your feature
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is under the MIT license. See the `LICENSE` file for more details.

## Author

Developed with ❤️ in Python
[MIT License](LICENSE)