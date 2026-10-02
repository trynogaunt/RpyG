# Python RPG Game


<pre align="center">
██████╗    ██████╗   ██╗   ██╗   ██████╗ 
██╔══██╗   ██╔══██╗  ╚██╗ ██╔╝  ██╔════╝ 
██║  ██║   ██████╔╝   ╚████╔╝   ██║  ███╗
██████╔╝   ██╔═══╝     ╚██╔╝    ██║   ██║
██╔══██╗   ██║          ██║     ██║   ██║
██║  ██║   ██║          ██║     ╚██████╔╝
╚═╝  ╚═╝   ╚═╝          ╚═╝      ╚═════╝ 

Your CPU will handle all the dragons.
</pre>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)
![Game Type](https://img.shields.io/badge/Game-Text--Based%20RPG-blueviolet)
![Status](https://img.shields.io/badge/Status-Work--in--Progress-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Last Commit](https://img.shields.io/github/last-commit/trynogaunt/RPyG)
[![Chat](https://img.shields.io/badge/Community-Join%20us!-blue?logo=github)](../../discussions)
![Code Style](https://img.shields.io/badge/code%20style-black-black)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
![Release](https://img.shields.io/badge/Release-Pre--Alpha-red)
[![pypresence](https://img.shields.io/badge/Discord-pypresence-00bb88.svg?logo=discord)](https://github.com/qwertyquerty/pypresence)


# RPyG - Retro Python Command Line RPG

#### RPyG is a **retro console Role-Playing-Game** written in Python
#### Inspired by old-school **MUD** adventures

> Early development stage, contributions welcome!

⭐ If you like the project, give it a star, it really helps!

## Features (current)

- Character creation (name + stat points)
- Explorable zones with multiple rooms, movement and "look around"
- Save and load with multiple slots
- Two interfaces: a [Textual](https://textual.textualize.io/) TUI and a plain console fallback
- Localization: English, French, German and Spanish

More gameplay is coming:
- Enemies & combat
- Inventory & items
- NPC & Shop system

## Installation

```bash
git clone https://github.com/trynogaunt/RPyG.git
cd RPyG

# Create and activate venv (optional, but recommended)
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # macOS / Linux

# Install the game and its dependencies
pip install -e .
```

With [uv](https://docs.astral.sh/uv/): `uv sync`.

## Run the game

```bash
rpyg                  # default interface
rpyg --ui textual     # Textual TUI
rpyg --ui console     # plain console
```

If Textual is not available, the game falls back to the console interface.

## Saves

Saves are stored as JSON files, one per slot, in your user data folder
(for example `~/.local/share/rpyg/saves` on Linux).

## Development

```bash
pytest
```

The game logic (`Game`) never prints or reads input: interfaces send actions
and render the views it returns, which is what lets several interfaces share
the same core.

## Full documentation

Coming soon on the Wiki
