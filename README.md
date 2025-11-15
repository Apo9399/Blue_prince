# The Blue Prince - Projet POO / Jeu de Manoir Procédural

Ce projet implémente une version jouable simplifiée du jeu "The Blue Prince".  
Le joueur explore un manoir généré progressivement, en plaçant de nouvelles pièces à mesure qu'il avance.


## 08/11/2025
---

## Structure du projet

├── main.py # Lance le jeu
├── game.py # Gère l'écran actif et la navigation entre écrans
├── moteur.py # Logique centrale du jeu (gameplay)
├── interface.py # Interface graphique (affichage + contrôles)
├── inventaire.py # Gestion des ressources et objets du joueur
└── assets/ # Images (pièces, icônes, joueur...)

---

## Fonctionnalités implémentées

### 1) **Inventaire du joueur**
Fichier : `inventaire.py`

Le joueur possède plusieurs ressources :
- Pas (points de déplacement)
- Pièces d’or
- Gemmes
- Clés
- Dés
- Objets permanents (ex : outils)

Fonctions incluses :
- Ajouter / dépenser / vérifier les ressources
- Ajouter et utiliser des objets permanents
- Empêcher les ressources de devenir négatives

---

### 2) **Manoir à génération progressive**
Fichier : `moteur.py`

Le manoir est une grille **5 colonnes × 9 lignes**.  
Chaque case peut contenir une pièce.  
Le joueur commence sur la salle d’entrée.

Quand il tente de se déplacer vers une case vide :
1. Le moteur tire **3 pièces aléatoires**.
2. L’interface affiche un **écran de choix**.
3. Le joueur choisit une pièce à placer.
4. La nouvelle pièce est placée dans la direction du déplacement.

---

### 3) **Déplacement du joueur**
- Contrôles : `ZQSD`
- Chaque déplacement consomme **1 pas**
- Le joueur peut se déplacer dans les pièces déjà placées
- Si la case visée est vide → la porte doit être "ouverte" → choix d’une nouvelle salle

---

### 4) **Sélection d’une nouvelle salle**
Fichiers : `moteur.py` + `interface.py` (RoomChoiceScreen)

- La touche `ESPACE` tente d'ouvrir une porte
- Le moteur renvoie une liste de 3 pièces possibles
- L’interface affiche un **écran de sélection**
- La sélection place la pièce dans la **bonne direction**, selon la touche de déplacement utilisée

---

### 5) **Système d’événements de pièce (simplifié)**
Lorsque le joueur entre dans une nouvelle salle, des effets peuvent se produire :
- Gain / perte de pas
- Gain / perte de gemmes
- Obtention d’objets (ex : clés)

Ces effets sont déclenchés dans la méthode :
piece.on_enter(logic)

---

### 6) **Affichage graphique**
Fichier : `interface.py`

- Grille affichée en vue du dessus
- Position du joueur indiquée par un contour jaune
- Interface d’inventaire affichée sur la droite
- Système d’écran basé sur une classe abstraite `AbstractScreen`
- Permet de changer d’écran sans mélanger UI et logique

---

## Comment jouer

| Action | Touche |
|-------|--------|
| Se déplacer | Z Q S D |
| Ouvrir une porte / Confirmer | ESPACE |
| Valider le choix de pièce | ENTRÉE |
| Quitter le jeu | Fermer la fenêtre |

Objectif : explorer le manoir avant que les **pas** ne tombent à 0.

---

## Points restants à développer

- Gestion des portes verrouillées (Clés / Crochetage)
- Vraies images pour les pièces
- Système de victoires / défaites
- Plus de types d’événements de pièces



