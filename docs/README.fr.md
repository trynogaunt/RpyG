# Python RPG Game

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Sommaire
- Description
- Installation
- Fonctionnalités
- Structure du projet
- Roadmap
- Contribution
- Licence

---

## Description

Jeu RPG textuel en Python avec interface console.  
Le joueur crée son personnage puis explore un monde composé de salles interconnectées.

🎯 Objectif actuel : établir un socle solide pour un RPG extensible  
(exploration, combat, quêtes, équipement, sauvegarde).

Fonctionnalités déjà en place :

- Menu principal interactif
- Création de personnage avec allocation de points
- Interface console stylisée via UIController
- Boucle de jeu (Game Loop) structurée avec machine d’état
- Room de départ + actions contextuelles d’exploration

---

## Installation

Cloner le projet :

    git clone https://github.com/trynogaunt/RpyG
    cd RpyG

Lancer le jeu :

    python app.py

> ⚠️ Requis : Python 3.10+ (utilisation de match/case)

---

## Fonctionnalités

### ✔ Déjà Implémenté

| Système | Détails |
|--------|---------|
| Création du personnage | Nom + distribution des stats (Santé, Force, Vitesse, Chance) |
| UI Console | Rendu stylisé + menus interactifs |
| Game Loop | États : Exploration / Menu / Pause / Combat futur / Exit |
| Monde | Première room jouable + actions de base |
| Architecture modulaire | Séparée en Game / World / UI / Classes |

---

### 🔜 En cours de développement

- Navigation et connexions complètes entre rooms
- Gestion contextuelle des actions selon la salle
- (Ré)implémentation du système de combat
- Inventaire + équipement
- Sauvegarde / Chargement

---

## Structure du Projet

    RpyG/
    ├── app.py                      # Entrée du jeu + menus + lancement Game
    ├── game/
    │   ├── game.py                 # Classe Game + game loop (state machine)
    │   └── creation_flow.py        # Logique création de personnage
    ├── world/
    │   ├── room.py                 # Classe Room
    │   ├── world.py                # Conteneur du monde
    │   └── build_world.py          # Construction de la map de base
    ├── classes/
    │   ├── character.py            # Classe parente
    │   ├── hero.py                 # Classe Hero (stats + état + position)
    │   ├── enemy.py                # Classe Enemy 
    │   └── interface_class.py      # État temporaire création du héros
    ├── ui/
    │   ├── ui_controller.py        # Gestion du rendu textuel
    │   └── screens/                # Écrans du menu principal / création
    └── README.md

> Anciennes classes inventaire/ennemis en refonte complète.

---

## Roadmap

### 🧱 Phase 1 — Exploration (actuelle)
- [x] Création personnage
- [x] Game Loop avec machine d’état
- [x] Spawn dans une salle jouable
- [ ] Mouvement NSEW entre salles
- [ ] Rencontres aléatoires lors des déplacements

### ⚔️ Phase 2 — Combat & Équipement
- [ ] Combat au tour par tour
- [ ] Calcul des dégâts selon stats (Force / Chance)
- [ ] Gestion équipements + inventaire
- [ ] Loot simple

### 💾 Phase 3 — Persistance
- [ ] Sauvegarde / Chargement
- [ ] Journal d’action
- [ ] Tests unitaires

### 🔮 Idées futures
- Génération procédurale des donjons
- Système de quêtes + PNJ
- Compétences et arbres de talents
- Mode rogue-lite optionnel

---

## Contribution

Les contributions sont les bienvenues 🎯

1. Fork le repo
2. Crée ta branche feature
3. Commit tes changements
4. Pull Request 🚀

---

## Licence

Projet sous licence MIT → voir LICENSE.

---

## Auteur

Développé avec ❤️ en Python  
par **Trynogaunt**
