=========================
 README - Blue Prince
=========================

Ce fichier explique comment installer et lancer le jeu "Blue Prince", ainsi que les règles et les contrôles.

==== Objectif du Jeu ====

Votre but est d'atteindre l'"Antechamber" (la pièce finale) située tout en haut du manoir (case 2, 0).

Vous disposez d'un nombre limité de "pas". Chaque déplacement ou placement de pièce consomme des pas. Si votre compteur de pas tombe à zéro, la partie est terminée et vous avez perdu.

Pour progresser, vous devez explorer le manoir en ouvrant des portes vers des cases vides. Cela vous coûtera parfois des clés (si la porte est verrouillée) et vous proposera de choisir une nouvelle pièce à placer. Gérez bien votre or, vos gemmes (pour acheter des pièces) et vos clés pour survivre.


==== Comment Lancer le Jeu ====

1. Prérequis (Installation)
-----------------------------
Ce jeu nécessite la bibliothèque Pygame. Assurez-vous de l'avoir installée.
Si ce n'est pas le cas, ouvrez un terminal et tapez :
pip install pygame

2. Fichiers
-----------------------------
Assurez-vous que tous les fichiers du projet sont présents dans le même dossier :
- main.py
- game.py
- moteur.py
- interface.py
- inventaire.py
- (Et le dossier 'assets/' contenant toutes les images du jeu)

3. Lancement
-----------------------------
Pour jouer, exécutez le fichier 'main.py' en dernier :
python main.py


==== Contrôles du Jeu ====

--- Exploration (Écran principal) ---
 W : Se déplacer/Viser vers le HAUT
 S : Se déplacer/Viser vers le BAS
 A : Se déplacer/Viser vers la GAUCHE
 D : Se déplacer/Viser vers la DROITE
 ESPACE : Tenter d'ouvrir une porte (lorsque vous visez une case vide)

--- Choix de la Pièce (Draft) ---
 A / Flèche GAUCHE : Sélectionner la pièce de gauche
 D / Flèche DROITE : Sélectionner la pièce de droite
 ENTRÉE : Valider le choix et placer la pièce
 R : Relancer les 3 choix (coûte 1 dé)

--- Ramassage d'Objets (Ecran "Objects found") ---
 W / Flèche HAUT : Sélectionner l'objet au-dessus
 S / Flèche BAS : Sélectionner l'objet en dessous
 ESPACE : Ramasser l'objet sélectionné

--- Boutique (Ecran "Kitchen Shop") ---
 W / Flèche HAUT : Sélectionner l'objet au-dessus
 S / Flèche BAS : Sélectionner l'objet en dessous
 ESPACE : Acheter l'objet sélectionné
 ECHAP : Quitter la boutique