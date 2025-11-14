# Python RPG Game

[![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)


Un jeu de rôle (RPG) développé en Python avec un système de combat, d'inventaire et de progression de personnage.

## 📋 Description

Ce projet est un jeu RPG textuel où le joueur incarne un héros qui peut :
- Combattre des ennemis
- Gérer son inventaire d'armes, armures et consommables
- Progresser en niveau et améliorer ses statistiques
- Équiper différents types d'objets

## 🚀 Installation

1. Clonez ce repository :
```bash
git clone <https://github.com/trynogaunt/RpyG>
cd "RpyG"
```

2. Assurez-vous d'avoir Python 3.7+ installé :
```bash
python --version
```

3. Lancez le jeu :
```bash
python app.py
```

## 🎮 Fonctionnalités

### Classes de Base
- **Hero** : Personnage joueur avec statistiques (santé, force, défense)
- **Enemy** : Ennemis avec IA de combat
- **Item System** : Système d'objets complet
  - Armes (dégâts variables selon la force)
  - Armures (protection)
  - Consommables (potions de soin, etc.)

### Système de Combat
- Combat au tour par tour
- Calcul des dégâts basé sur les statistiques
- Système d'esquive et de critique

### Inventaire
- Gestion des objets
- Équipement d'armes et armures
- Utilisation de consommables

## 📁 Structure du Projet

```
RPyG/
├── classes/
│   ├── hero.py          # Classe Hero
│   ├── enemy.py         # Classe Enemy  
│   ├── Item.py          # Système d'objets
│   └── inventory.py     # Gestion inventaire
├── main.py              # Point d'entrée du jeu
├── README.md
└── .gitignore
```

## 🎯 Utilisation

```python
# Exemple de création d'un héros
from classes.hero import Hero
from classes.Item import Weapon

hero = Hero("Aventurier", 100, 20, 10)
épée = Weapon("Épée d'Acier", "Une épée tranchante", 15, 0.1)
hero.attack(enemy)
```

## 🛠️ Technologies

- **Python 3.7+**
- Programmation Orientée Objet (POO)
- Architecture modulaire avec classes séparées

## 🚧 En Développement

- Sauvegarde/Chargement
- Effets d'armes spéciaux

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## ✨ Auteur

Développé avec ❤️ en Python