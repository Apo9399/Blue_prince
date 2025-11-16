# moteur.py
import random
from inventaire import Inventaire


# ─────────────────────────────────────────────
# Données simples utilisés pour simuler des pièces
# ─────────────────────────────────────────────

class Piece:
    """Représente une pièce simple du manoir."""

    def __init__(self, nom, image_name, gem_cost, doors, loot=None, effect=None,rarity="B"):
        """
        Initialise une nouvelle pièce du manoir.

        Args:
            nom (str): Nom de la pièce (ex: 'Pantry', 'Kitchen').
            image_name (str): Nom de l'image à afficher dans l'interface.
            gem_cost (int): Coût en gemmes pour placer la pièce.
            doors (dict): Dictionnaire indiquant la présence de portes {"N": bool, "S": bool, "E": bool, "W": bool}.
            loot (dict, optional): Butin fixe attribué lors de l'entrée (or/gemmes/dés/clé). Default: None.
            effect (str, optional): Nom d'un effet spécial appliqué lors de l'entrée (ex: 'ballroom').
            rarity (str): Rareté de la pièce ('B','G','Y','V','O').
        """
        self.nom = nom
        self.image_name = image_name
        self.gem_cost = gem_cost
        
        # doors par exemple : {"N": True, "S": False, "E": True, "W": False}
        self.doors = doors  

        # Angle de rotation actuel (utilisé pour la rotation de l’image).
        self.rotation = 0
        
        # Butin (or / gemmes / dés / clés) gagné en entrant dans la pièce
        # loot est un dict comme {"gold": 0, "gems": 0, "dice": 0, "keys": 0}
        self.loot = loot or {"gold": 0, "gems": 0, "dice": 0, "keys": 0}

        # Champ générique pour des effets spéciaux (Ballroom, Corridor, etc.)
        self.effect = effect

        # Pour ne donner le butin qu'une seule fois
        self.loot_taken = False
        
        self.items = []  # objets présents dans cette pièce
        self.items_taken = False   
        
        #rarement de la piece
        self.rarity = rarity


    def rotate_90(self):
        """
        Fait pivoter la pièce de 90° dans le sens horaire et met à jour l'orientation des portes.

        Returns:
            None
        """
        new_doors = {
            "N": self.doors["W"],
            "E": self.doors["N"],
            "S": self.doors["E"],
            "W": self.doors["S"]
        }
        self.doors = new_doors
        self.rotation = (self.rotation + 90) % 360
        

    def clone(self):
        """
        Crée un clone indépendant de la pièce (avec portes, loot et rotation identiques).

        Returns:
            Piece: Une copie profonde de la pièce actuelle.
        """
        new = Piece(
            self.nom,
            self.image_name,
            self.gem_cost,
            self.doors.copy(),
            loot=self.loot.copy(),
            effect=self.effect,
            rarity=self.rarity
        )
        new.rotation = self.rotation
        # Quand on clone une carte, le butin de cette nouvelle tuile
        # n'a pas encore été ramassé
        new.items = self.items.copy()    
        new.items_taken = self.items_taken    

        new.loot_taken = self.loot_taken 
        
        return new


# ─────────────────────────────────────────────
# Manoir = grille (5 colonnes × 9 lignes)
# ─────────────────────────────────────────────

class Manoir:
    """Représente la grille du manoir (5 colonnes × 9 lignes)."""
    def __init__(self, rows=9, cols=5):
        """
        Initialise la grille du manoir.

        Args:
            rows (int): Nombre de lignes (default = 9).
            cols (int): Nombre de colonnes (default = 5).
        """
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]

    def get_piece(self, pos):
        """
        Retourne la pièce située à la position donnée.

        Args:
            pos (tuple): (col, row)

        Returns:
            Piece or None: La pièce à cette position, ou None si vide.
        """
        col, row = pos
        return self.grid[row][col]

    def set_piece(self, pos, piece):
        """
        Place une pièce dans la grille à une position donnée.

        Args:
            pos (tuple): (col, row)
            piece (Piece): La pièce à placer.

        Returns:
            None
        """
        col, row = pos
        self.grid[row][col] = piece

    def is_inside(self, pos):
        """
        Vérifie si une position est dans les limites de la grille.

        Args:
            pos (tuple): (col, row)

        Returns:
            bool: True si la position est valide, sinon False.
        """
        col, row = pos
        return 0 <= col < self.cols and 0 <= row < self.rows


# ─────────────────────────────────────────────
# Joueur
# ─────────────────────────────────────────────

class Joueur:
    """Représente le joueur dans le manoir (position et déplacement)."""
    def __init__(self, start_position):
        """
        Initialise la position du joueur.

        Args:
            start_position (tuple): Position initiale (col, row).
        """
        self.position = start_position  # tuple (col, row)

    def move(self, direction):
        """
        Calcule la nouvelle position du joueur en fonction de la direction.

        Args:
            direction (str): 'UP', 'DOWN', 'LEFT', 'RIGHT'.

        Returns:
            tuple: Nouvelle coordonnée proposée (col, row). 
                   Le moteur décidera si ce déplacement est valide.
        """
        col, row = self.position

        if direction == "UP":
            row -= 1
        elif direction == "DOWN":
            row += 1
        elif direction == "LEFT":
            col -= 1
        elif direction == "RIGHT":
            col += 1

        return (col, row)  # retour de la position candidate


# ─────────────────────────────────────────────
# Objet retourné quand on tente d'ouvrir une porte
# (utilisé par interface → pour afficher l’écran de choix)
# ─────────────────────────────────────────────

class TryOpenDoorResult:
    """
    Représente le résultat d'une tentative d'ouverture de porte.
    Utilisé par l'interface pour savoir :
      - s'il faut afficher le choix de pièces,
      - quelles options sont disponibles,
      - s'il faut afficher un message spécial.
    """
    def __init__(self, needs_room_choice=False, room_options=None,message=""):
        """
        Args:
            needs_room_choice (bool): True si le joueur doit choisir une nouvelle pièce.
            room_options (list[Piece]): Liste de pièces proposées à l'écran.
            message (str): Message d'erreur ou d'information.
        """
        self.needs_room_choice = needs_room_choice
        self.room_options = room_options or []
        self.message = message 

# ─────────────────────────────────────────────
# GameLogic (le moteur)
# ─────────────────────────────────────────────

class GameLogic:
    """
    Moteur central du jeu.

    Cette classe regroupe la totalité de la logique interne :
        - Gestion du manoir (grille, placement et rotation des pièces).
        - Gestion du joueur (position, déplacements, portes).
        - Système de tirage de tuiles (3 cartes → choix du joueur).
        - Rareté des pièces et pondération du tirage.
        - Gestion du loot fixe et du loot aléatoire.
        - Gestion des objets, consommables, keys, pas, gemmes.
        - Système de portes verrouillées (lock 0 / lock 1 / lock 2).
        - Application des effets spéciaux des pièces (Ballroom, Kitchen, etc.).
        - Systèmes annexes :
                * Reroll via dés
                * Téléportations
                * Inventaire joueur
                * Conditions de victoire et défaite
        - Interaction avec l’interface (GameScreen, PickItemScreen, PurchaseItemScreen).

    Le GameLogic ne dessine rien :
    → Il fournit uniquement l’état du jeu et les actions possibles.
    L’interface utilise GameLogic comme API pour afficher l’état et répondre au joueur.
    """
    def __init__(self):
        """
        Initialise la totalité de l'état interne du jeu ainsi que les ressources
        nécessaires au moteur.

        Composants initialisés :

            1. Inventaire du joueur
                - pièces d'or
                - gemmes
                - clés
                - dés
                - pas
                - objets spéciaux (lockpick, rabbit foot, metal detector)

            2. Structure du manoir (Manoir)
                - Grille vide 5 × 9
                - Pièce d'entrée (Entrée) placée en bas au centre
                - Pièce finale (Antechamber) placée en haut

            3. Joueur
                - Position initiale (col=2, row=8)
            
            4. Pool d’objets aléatoires (drop aléatoire 80%)
                - coins / gems / keys / dice
                - apple / carrot / meat
                - lockpick / rabbit foot / metal detector

            5. Réglages de nourriture
                - steps gagnés
                - prix en or

            6. Rareté des pièces
                - Poids définis pour : B, G, Y, V, O

            7. Catalogue complet des pièces du jeu
                - Chaque salle est une instance de Piece
                - Chaque salle inclut :
                    * nom
                    * icône
                    * coût en gemmes
                    * portes
                    * loot fixe
                    * effet spécial (facultatif)
                    * rareté

            8. Gestion interne des portes verrouillées
                - self.doors : dictionnaire stockant les niveaux des verrous
                - Le niveau est créé dynamiquement lors de la tentative d’ouverture

            9. État global du jeu
                - last_move_dir : dernière direction visée
                - game_over / player_won
                - last_effect_message (pour affichage interface)
                - game_context, image_manager → référencés par l’interface

        Le constructeur prépare tout le moteur pour permettre :
            → le déplacement
            → le placement de nouvelles pièces
            → la gestion du loot
            → l’application des effets
            → l’ouverture des interfaces
            → les conditions de victoire/défaite

        Aucun dessin n’est réalisé ici.
        Le moteur est immédiatement utilisable après cette initialisation.
        """
        # Inventaire
        self.inventaire = Inventaire()

        # Carte
        self.manoir = Manoir()

        # Position de départ → milieu ligne du bas
        self.joueur = Joueur(start_position=(2, 8))

        # --- CORRECTION ---
        # 1. Créer pièce de départ (une seule fois)
        # (Chemin simple, car l'image est DANS assets/)
        start_room = Piece("Entrée", "Entrance_Hall_Icon.png", 0, {"N": True, "S": False, "E": True, "W": True})
        self.manoir.set_piece(self.joueur.position, start_room)
        
        # 3. Creer piece de terminus
        self.antechamber_pos = (2, 0)
        antechamber = Piece("Antechamber", "Antechamber_Icon.png", 0, {"N": False, "S": True, "E": True, "W": True})
        self.manoir.set_piece(self.antechamber_pos, antechamber)
        # ---------------------------------------------------------
        # Pool d’objets aléatoires (utilisé pour la génération aléatoire lors de l’entrée dans une pièce).
        # ---------------------------------------------------------
        self.item_pool = {
            "coins": 0.10,
            "gems": 0.07,
            "keys": 0.08,
            "dice": 0.05,

            # food
            "apple": 0.20,
            "carrot": 0.18,
            "meat": 0.12,

            # tools
            "lockpick": 0.10,
            "rabbit_foot": 0.05,
            "metal_detector": 0.05,
        }

        # food list
        self.food_steps = {
            "apple": 1,
            "carrot": 2,
            "meat": 3
        }
        
        #food price
        self.food_prices = {
            "apple": 3,
            "carrot": 5,
            "meat": 8
        }

        
        # ---------------------------------------------------------
        #  Poids de rareté (selon la couleur de la pièce).
        # ---------------------------------------------------------
        self.rarity_weights = {
            "B": 30,   # Blue
            "G": 30,   # Green
            "Y": 20,   # Yellow
            "V": 10,   # Violet
            "O": 10    # Orange
        }



        # 2. Créer le catalogue de pièces à tirer
        # (Chemins simples, car les images sont DANS assets/)
        self.catalogue = [
            # Salles Bleues (Blue → B)
            Piece("Pantry", "Pantry_Icon.png", 0,
                {"N": False, "S": True, "E": False, "W": True},
                loot={"gold": 4, "gems": 0, "dice": 0, "keys": 0},
                rarity="B"),
            Piece("Walk-in Closet", "Walk-in_Closet_Icon.png", 1,
                {"N": False, "S": True, "E": False, "W": False},
                rarity="B"),
            Piece("Ballroom", "Ballroom_Icon.png", 1,
                {"N": True, "S": True, "E": False, "W": False},
                effect="ballroom",
                rarity="B"),
            Piece("Billiard_room", "Billiard_Room_Icon.png", 1,
                {"N": False, "S": True, "E": False, "W": True},
                rarity="B"),
            Piece("Aquarium", "Aquarium_Icon.png", 3,
                {"N": False, "S": True, "E": True, "W": True},
                rarity="B"),
            Piece("DiningRoom", "Dining_Room_Icon.png", 1,
                {"N": False, "S": True, "E": True, "W": True},
                rarity="B"),
            Piece("Gallery", "Gallery_Icon.png", 1,
                {"N": True, "S": True, "E": False, "W": False},
                loot={"gold": 0, "gems": 3, "dice": 0, "keys": 0},
                rarity="B"),
            Piece("Garage", "Garage_Icon.png", 1,
                {"N": False, "S": True, "E": False, "W": False},
                loot={"gold": 0, "gems": 0, "dice": 0, "keys": 3},
                rarity="B"),
            Piece("LockerRoom", "Locker_Room_Icon.png", 0,
                {"N": True, "S": True, "E": False, "W": False},
                loot={"gold":0,"gems":0,"dice":0,"keys":1},
                effect="locker_room",
                rarity="B"),
            Piece("Nook", "Nook_Icon.png", 0,
                {"N": False, "S": True, "E": False, "W": True},
                loot={"gold": 0, "gems": 0, "dice": 0, "keys": 1},
                rarity="B"),
            Piece("Room8", "Room_8_Icon.png", 0,
                {"N": False, "S": True, "E": False, "W": True},
                rarity="B"),
            Piece("RumpusRoom", "Rumpus_Room_Icon.png", 0,
                {"N": True, "S": True, "E": False, "W": False},
                loot={"gold": 8, "gems": 0, "dice": 0, "keys": 0},
                rarity="B"),
            Piece("TrophyRoom", "Trophy_Room_Icon.png", 0,
                {"N": False, "S": True, "E": False, "W": True},
                loot={"gold": 0, "gems": 8, "dice": 0, "keys": 0},
                rarity="B"),
            Piece("WineCellar", "Wine_Cellar_Icon.png", 1,
                {"N": False, "S": True, "E": False, "W": False},
                loot={"gold": 0, "gems": 3, "dice": 0, "keys": 0},
                rarity="B"),

            # Salles Vertes (Green → G)
            Piece("Secret_Garden", "Secret_Garden_Icon.png", 1,
                {"N": False, "S": True, "E": True, "W": True},
                rarity="G"),
            Piece("Veranda", "Veranda_Icon.png", 2,
                {"N": True, "S": True, "E": False, "W": False},
                rarity="G"),

            # Salles Dorées (Gold/Yellow → Y)
            Piece("Kitchen", "Kitchen_Icon.png", 2,
                {"N": False, "S": True, "E": False, "W": True},
                rarity="Y"),
            Piece("Showroom", "Showroom_Icon.png", 3,
                {"N": True, "S": True, "E": False, "W": False},
                rarity="Y"),

            # Salles Violet (Purple → V)
            Piece("BunkRoom", "Bunk_Room_Icon.png", 0,
                {"N": False, "S": True, "E": False, "W": False},
                rarity="V"),
            Piece("LadyChamber", "Her_Ladyship's_Chamber_Icon.png", 0,
                {"N": False, "S": True, "E": False, "W": False},
                rarity="V"),

            # Salles Orange (Orange → O)
            Piece("Corridor", "Corridor_Icon.png", 0,
                {"N": True, "S": True, "E": False, "W": False},
                rarity="O"),
            Piece("EastWingHall", "East_Wing_Hall_Icon.png", 0,
                {"N": False, "S": True, "E": True, "W": True},
                rarity="O"),
            Piece("GreatHall", "Great_Hall_Icon.png", 0,
                {"N": True, "S": True, "E": True, "W": True},
                loot={"gold": 5, "gems": 5, "dice": 0, "keys": 0},
                rarity="O"),
            Piece("Passageway", "Passageway_Icon.png", 0,
                {"N": True, "S": True, "E": True, "W": True},
                rarity="O"),
            Piece("Secretpassage", "Secret_Passage_Icon.png", 0,
                {"N": False, "S": True, "E": False, "W": False},
                rarity="O")
        ]




        # Memoire de la direction
        self.last_move_dir = None
        
        # Etat du jeu
        self.game_over = False
        self.player_won = False
        
        #la porte
        self.doors = {}
        
        # message
        self.move_message = ""
        
        
        self.game_context = None
        self.image_manager = None
        self.last_effect_message = ""



    # ────────────────────────────────
    # GETTERS pour interface.py
    # ────────────────────────────────
    def get_player_position(self):
        return self.joueur.position

    def get_steps(self):
        return self.inventaire.pas

    def get_gold(self):
        return self.inventaire.pieces_or

    def get_gems(self):
        return self.inventaire.gemmes

    def get_keys(self):
        return self.inventaire.cles

    def get_dice(self):
        return self.inventaire.des

    def has_item(self, nom_objet):
        return self.inventaire.a_objet(nom_objet)

    # ────────────────────────────────
    # Déplacement du joueur
    # ────────────────────────────────
    def move_player(self, direction):
        """
        Déplace le joueur dans une direction et gère les règles de déplacement.
        
        Ce comportement inclut :
            - Vérification que le mouvement reste dans la grille.
            - Vérification des portes entre la pièce actuelle et la pièce cible.
            - Détection des collisions avec des murs.
            - Consommation automatique des pas si le déplacement est valide.
            - Activation des effets liés à l'entrée dans une pièce déjà existante.
            - Déclenchement des conditions de fin de jeu.
        
        Args:
            direction (str): Direction du déplacement.
                            Valeurs possibles : "UP", "DOWN", "LEFT", "RIGHT".
        
        Returns:
            None:
                → Le moteur met simplement à jour la position du joueur
                ou refuse le déplacement selon les règles des portes.
        """
        self.last_move_dir = direction  # Enregistre la direction visée

        new_pos = self.joueur.move(direction)

        # 1. Vérifie si la case est dans la grille
        if not self.manoir.is_inside(new_pos):
            return
        
        # ─────────────────────────────────────────
        # 2. Si la case contient une pièce → vérifier portes !
        # ─────────────────────────────────────────
        current_room = self.manoir.get_piece(self.joueur.position)
        target_room = self.manoir.get_piece(new_pos)

        dir_map = {"UP":"N", "DOWN":"S", "LEFT":"W", "RIGHT":"E"}
        cardinal = dir_map[direction]

        opposite = {"N":"S", "S":"N", "E":"W", "W":"E"}
        opposite_card = opposite[cardinal]
        
        if current_room.doors.get(cardinal, False):
            self.move_message = ""
        
        if target_room is not None:

            # Si la pièce actuelle n'a pas de porte → interdit
            if not current_room.doors.get(cardinal, False):
                self.move_message = "There is a wall in that direction."
                return

            # Si la pièce cible n'a pas la porte opposée → interdit
            if not target_room.doors.get(opposite_card, False):
                self.move_message = "There is a wall in that direction."
                return

            # Sinon déplacement valide
            self.joueur.position = new_pos
            self.inventaire.perdre_pas()
            
            #Calculer les butins et les effets lors de l’entrée dans une nouvelle pièce.
            self.on_enter_room()

            self.check_end_conditions()
            self.move_message = ""
            return


            # 3. Si la case est vide (None)
            # Le joueur ne bouge PAS.
            # Le jeu attend que le joueur appuie sur ESPACE.
        
        return

    def draw_room_by_rarity(self, playable):
        """
        Tire aléatoirement une pièce parmi la liste des pièces plaçables,
        pondéré par leur rareté.

        Les raretés sont traduites en poids via self.rarity_weights :
            B (Blue)   : 30
            G (Green)  : 30
            Y (Yellow) : 20
            V (Violet) : 10
            O (Orange) : 10

        Args:
            playable (list[Piece]): Liste de pièces compatibles avec
                                    l’emplacement ciblé (rotation incluse).

        Returns:
            Piece: Une pièce sélectionnée aléatoirement selon les poids de rareté.
        """
            
        # Extraire la rareté correspondante.
        rarities = [p.rarity for p in playable]

        # Convertir la rareté en poids.
        weights = [self.rarity_weights[r] for r in rarities]

        # Sélectionner une pièce aléatoirement selon la rareté.
        return random.choices(playable, weights=weights, k=1)[0]

    # ────────────────────────────────
    # Tentative d’ouvrir une porte → tirage des 3 pièces
    # ────────────────────────────────
    def try_open_door(self):
        """
        Gère la logique d'ouverture d'une porte dans la direction visée.

        Comportements inclus :
            - Vérification de la direction visée.
            - Vérification qu’on reste dans la grille.
            - Gestion d’un passage vers une pièce existante
                → Si la pièce existe déjà :
                    * Vérification des portes
                    * Déplacement direct sans tirage
                    * Application des effets de la pièce
            - Gestion d’un passage vers une case vide :
                * Vérification des portes nécessaires.
                * Vérification/Création du niveau de verrou (lock 0, 1 ou 2).
                * Consommation éventuelle d’une clé ou usage d’un lockpick.
                * Recherche de toutes les pièces plaçables (avec rotation).
                * Sélection de 3 pièces :
                    1. Une pièce gratuite obligatoirement.
                    2. Deux pièces supplémentaires, noms différents.
                * Pondération par la rareté.

        Returns:
            TryOpenDoorResult:
                - needs_room_choice = True si le joueur doit choisir parmi 3 pièces.
                - room_options = liste de 3 pièces proposées.
                - message = texte à afficher s'il y a un blocage ou un avertissement.
        """
        # Sécurité: Ne fait rien si le joueur n'a pas visé une direction
        if self.last_move_dir is None:
            return TryOpenDoorResult(needs_room_choice=False)
            
        # Sécurité: Vérifie si la case visée est valide
        new_pos = self.joueur.move(self.last_move_dir)
        if not self.manoir.is_inside(new_pos):
            self.last_move_dir = None # Réinitialise la direction
            return TryOpenDoorResult(needs_room_choice=False)
            
        # Sécurité: Vérifie si la case n'est pas déjà prise
        neighbor = self.manoir.get_piece(new_pos)
        if neighbor is not None:
            # La pièce actuelle doit avoir une porte dans cette direction
            dir_map = {"UP": "N", "DOWN": "S", "LEFT": "W", "RIGHT": "E"}
            cardinal = dir_map[self.last_move_dir]

            # Porte opposée
            opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
            opp = opposite[cardinal]

            # S'il manque une porte, on bloque
            if not neighbor.doors.get(opp, False):
                self.last_move_dir = None
                return TryOpenDoorResult(
                    needs_room_choice=False,
                    message="The next room has no matching door."
                )

            # Sinon passage normal
            self.joueur.position = new_pos
            self.inventaire.perdre_pas()
            
            # Entrée dans une pièce déjà existante
            self.on_enter_room()
            
            self.check_end_conditions()
            self.last_move_dir = None
            return TryOpenDoorResult(needs_room_choice=False)


        # Vérifier si la pièce actuelle possède des portes.
        current_x, current_y = self.joueur.position
        room = self.manoir.get_piece((current_x, current_y))

        # Mapper les directions.
        dir_map = {"UP": "N", "DOWN": "S", "LEFT": "W", "RIGHT": "E"}
        dir_needed = dir_map[self.last_move_dir]

        # S’il n’y a pas de porte dans cette direction pour la pièce → bloqué.
        if not room.doors.get(dir_needed, False):
            self.last_move_dir = None
            return TryOpenDoorResult(
                needs_room_choice=False,
                message="There is no door in that direction."
            )
        
        # Vérifier/générer le niveau du verrou de la porte.
        lock_level = self._get_or_create_door_lock(self.joueur.position, new_pos)

        room_target = self.manoir.get_piece(new_pos)
        room_current = self.manoir.get_piece(self.joueur.position)
        
        # Logique des clés / outils de déverrouillage.
        need_key = False
        if lock_level == 0:
            need_key = False
        elif lock_level == 1:
            # Avec un crochet de serrure (Lockpick), il est possible de ne pas consommer de clé.
            if self.inventaire.a_objet("lockpick"):
                self.last_action_message = "Tu as utilisé un crochet de serrure."
                return True

            # --- Sinon: cle obligatoire ---
            if self.inventaire.depenser_cles(1):
                self.last_action_message = "Tu as utilisé une clé"
                return True
            else:
                self.last_action_message = "Tu n’as ni clé ni crochet de serrure !"
                return False
        elif lock_level == 2:
            # Un verrou de niveau 2 doit obligatoirement être ouvert avec une clé.
            need_key = True
        # Corridor rule: doors to Corridor never require keys
        if room_target and room_target.nom == "Corridor":
            need_key = False
        if room_current and room_current.nom == "Corridor":
            need_key = False


        if need_key:
            if not self.inventaire.depenser_cles(1):
                msg = "You need a key or a lockpick to open this door."
                print(f"Porte verrouillée (niveau {lock_level}) : pas assez de clés.")
                # Impossible d’ouvrir la porte, retourner directement « aucune pièce choisie ».
                self.last_move_dir = None
                return TryOpenDoorResult(
                            needs_room_choice=False,
                            message=msg
                        )

        
        
        
        
        # ============================================================
        #  NOUVEAU : Tirage uniquement parmi les pièces réellement
        #  plaçables → avec rotation automatique.
        # ============================================================

        direction = self.last_move_dir
        player_pos = self.joueur.position

        # Cherche toutes les variantes jouables (0, 90°, 180°, 270°)
        def get_valid_rotation(template):
            p = template.clone()
            for _ in range(4):
                if self.piece_is_placeable(p, player_pos, direction):
                    return p   # 
                p.rotate_90()
            return None


        # Liste de toutes les pièces jouables
        playable = []

        for templ in self.catalogue:
            fixed = get_valid_rotation(templ)
            if fixed is not None:
                playable.append(fixed)


        # Si aucune pièce ne peut être placée → message
        if not playable:
            self.last_move_dir = None
            return TryOpenDoorResult(
                needs_room_choice=False,
                message="No possible room can be placed here."
            )

        # -------------------------
        # Toujours garantir un room 0 gemme
        # -------------------------
        playable_free = [p for p in playable if p.gem_cost == 0]

        if not playable_free:
            self.last_move_dir = None
            return TryOpenDoorResult(
                needs_room_choice=False,
                message="No free room can be placed here."
            )

        # 1) d'abord une gratuite
        r1 = self.draw_room_by_rarity(playable_free)
        
        chosen_names = {r1.nom}

        # 2) puis deux autres (noms différents)
        pool2 = [p for p in playable if p.nom not in chosen_names]
        
        r2 = self.draw_room_by_rarity(pool2)
        chosen_names.add(r2.nom)
        
        pool3 = [p for p in playable if p.nom not in chosen_names]

        r3 = self.draw_room_by_rarity(pool3)
        chosen_names.add(r3.nom)

        room_options = [r1, r2, r3]
        random.shuffle(room_options)

        return TryOpenDoorResult(
            needs_room_choice=True,
            room_options=room_options
        )


    # ────────────────────────────────
    # Choix d’une pièce dans l’écran RoomChoice
    # ────────────────────────────────
    def select_room(self, piece):
        """
        Place la pièce choisie par le joueur et applique toutes les conséquences.

        Cette méthode est appelée depuis l'écran RoomChoice lorsqu’un joueur sélectionne
        l’une des 3 pièces proposées.

        Étapes détaillées :
        --------------------
        1. Vérifier que le joueur peut payer le coût en gemmes de la pièce.
        → Si insuffisant : retour False et annulé.

        2. Déterminer la position cible où la pièce doit être placée.
        Cette position dépend de :
            - la position actuelle du joueur
            - self.last_move_dir (UP / DOWN / LEFT / RIGHT)

        3. Placer la pièce dans la grille du manoir.
        - La nouvelle tuile remplace une case vide.
        - On pose un attribut « is_new = True » pour identifier une pièce fraîche.

        4. Déplacer le joueur dans cette pièce nouvellement placée.

        5. Dépenser un pas (step).

        6. Réinitialiser last_move_dir pour éviter des actions fantômes.

        7. Appeler on_enter_room(), ce qui :
            - distribue le loot fixe
            - applique les effets spéciaux
            - peut ouvrir PickItemScreen / PurchaseItemScreen
            - peut générer des objets aléatoires

        8. Vérifier conditions de victoire / défaite.

        9. Une fois toutes les logiques appliquées :
            Si aucune interface spéciale n’a été ouverte,
            → retour automatique au GameScreen via game_context.show_game_screen().

        Paramètres
        ----------
        piece : Piece
            La pièce choisie par le joueur parmi les 3 proposées.

        Retour
        ------
        bool
            True si la pièce a été placée et le joueur déplacé.
            False si l’opération a échoué (paiement impossible ou incohérence).
        """
        # 1. Tente de payer le coût en gemmes
        if not self.inventaire.depenser_gemmes(piece.gem_cost):
            print("Pas assez de gemmes!") # Message d'erreur
            return False

        # 2. Trouve la position où placer la pièce (basé sur la direction visée)
        col, row = self.joueur.position

        if self.last_move_dir == "UP":
            new_pos = (col, row - 1)
        elif self.last_move_dir == "DOWN":
            new_pos = (col, row + 1)
        elif self.last_move_dir == "LEFT":
            new_pos = (col - 1, row)
        elif self.last_move_dir == "RIGHT":
            new_pos = (col + 1, row)
        else:
            return False  # Ne devrait jamais arriver

        # 4. Place la pièce dans la grille
        self.manoir.set_piece(new_pos, piece)
        
        piece.is_new = True


        # 5. Déplace le joueur dans la nouvelle pièce
        self.joueur.position = new_pos

        # 6. Dépense un "pas"
        self.inventaire.perdre_pas()
        
        # 7. Réinitialise la direction
        self.last_move_dir = None
        
        # Entrée dans une pièce déjà existante
        self.on_enter_room()
        
        # 8. Placer une nouvelle pièce et vérifier la victoire après y être entré.
        self.check_end_conditions()
        
        # 8. Si aucune interface spéciale n'a été ouverte, retour à GameScreen
        from interface import PickItemScreen, PurchaseItemScreen

        # si c'est ni PickItemScreen ni PurchaseItemScreen → on retourne au jeu
        if not isinstance(self.game_context.current_screen, (PickItemScreen, PurchaseItemScreen)):
            self.game_context.show_game_screen()

        return True


    # ────────────────────────────────
    # Verifier si le jeu est terminer
    # ────────────────────────────────
    def check_end_conditions(self):
        # pas =0
        if self.inventaire.pas <= 0:
            self.game_over = True
            self.player_won = False
            return

        # arriver en terminus
        if self.joueur.position == self.antechamber_pos:
            self.game_over = True
            self.player_won = True
            return
        
    def on_enter_room(self):
        """
        Appelé à chaque fois que le joueur entre dans une pièce.
        Gère d'abord le butin fixe (or / gemmes / clés / dés).
        Plus tard on ajoutera ici les effets spéciaux (Ballroom, Corridor, etc.)
        """
        room = self.manoir.get_piece(self.joueur.position)
        if room is None:
            return

        # --- 1) Butin fixe : ne se déclenche qu'une seule fois par pièce ---
        loot = getattr(room, "loot", None)
        if loot and not getattr(room, "loot_taken", False):
            gold = loot.get("gold", 0)
            gems = loot.get("gems", 0)
            keys = loot.get("keys", 0)
            dice = loot.get("dice", 0)

            if gold > 0:
                self.inventaire.gagner_pieces(gold)
            if gems > 0:
                self.inventaire.gagner_gemmes(gems)
            if keys > 0:
                self.inventaire.gagner_cles(keys)
            if dice > 0:
                self.inventaire.gagner_des(dice)

            room.loot_taken = True  # on ne le donne qu'une fois

        # --- 2) Effets spéciaux (on les ajoutera dans les prochaines étapes) ---
        if room.effect:
            self.apply_room_effect(room)
            
        # -----------------------------------------------------
        #   Ne pas générer de loot dans Entrance Hall / Antechamber
        # -----------------------------------------------------
        if room.nom in ("Entrée", "Antechamber"):
            return
        
        if room.nom == "Kitchen":
            if not getattr(room, "is_shop", False):
                import random

                foods = ["apple", "carrot", "meat"]
                count = random.randint(1, 5)
                shop_items = random.choices(foods, k=count)

                room.shop_items = shop_items
                room.is_shop = True

                from interface import PurchaseItemScreen
                self.game_context.current_screen = PurchaseItemScreen(
                    self.game_context, self, self.image_manager, room
                )

                self.last_effect_message = "You entered Kitchen → Food shop opened"
            
            return
            
        # -----------------------------------------------------
        #   Génération aléatoire d'objets (0 à 3)
        # -----------------------------------------------------
        if not room.items_taken and not room.items:

            import random

            if random.random() < 0.80:  # Générer un objet avec une probabilité de 80 %.

                n = random.randint(1, 3)

                # Tirer un objet en fonction des poids.

                names = list(self.item_pool.keys())
                weights = list(self.item_pool.values())

                room.items = random.choices(names, weights, k=n)

            else:
                room.items = []

            
        # -----------------------------------------------------
        #   Si la pièce contient des objets → ouvrir l'écran de loot
        # -----------------------------------------------------
        # Si c’est une nouvelle pièce → autoriser le drop et la collecte.
        if getattr(room, "is_new", False):

            # Générer d’abord le drop.
            if not room.items_taken and not room.items:
                import random
                if random.random() < 0.80:
                    n = random.randint(1, 3)
                    names = list(self.item_pool.keys())
                    weights = list(self.item_pool.values())
                    room.items = random.choices(names, weights, k=n)
                else:
                    room.items = []

            # S’il y a un drop → ouvrir l’interface de collecte.
            if room.items and not room.items_taken:
                from interface import PickItemScreen
                self.game_context.current_screen = PickItemScreen(
                    self.game_context, self, self.image_manager, room
                )

            # Après l’ouverture de l’interface de collecte 
            # → la pièce devient immédiatement une ancienne pièce.
            room.is_new = False

        else:
            # Les anciennes pièces → ne déclenchent jamais de collecte.
            return





    # ────────────────────────────────
    # Creer le verrou
    # ────────────────────────────────
    
    def _get_or_create_door_lock(self, from_pos, to_pos):
        """
        Crée ou récupère un verrou pour une porte.
        Probabilités ajustées selon les étages :
        
        - Lignes 7-8 : 100% niveau 0
        - Lignes 0-1 : 100% niveau 2
        - Lignes 2-6 : probabilités réglables (voir tableau)
        """

        key = frozenset({from_pos, to_pos})
        if key in self.doors:
            return self.doors[key]

        _, r1 = from_pos
        _, r2 = to_pos
        min_row = min(r1, r2)

        # --- Zone basse : lignes 7-8 → 100% unlocked ---
        if min_row >= 4:
            lock_level = 0

        # --- Zone haute : lignes 0-1 → 100% verrou niveau 2 ---
        elif min_row <= 1:
            lock_level = 2

        # --- Zone centrale : lignes 2-6 → probas personnalisées ---
        else:
            # Ici tu modifies les probabilités comme tu veux :
            # poids pour [0, 1, 2]
            weights = {
                0: 0.95,   # 95% portes ouvertes
                1: 0.04,   # 4% verrou niveau 1
                2: 0.01    # 1% verrou niveau 2
            }

            lock_level = random.choices(
                population=[0, 1, 2],
                weights=[weights[0], weights[1], weights[2]],
                k=1
            )[0]

        # Sauvegarde du niveau
        self.doors[key] = lock_level
        return lock_level

    
    

    def get_current_door_message(self):
        """
        Pour l'interface : en fonction de last_move_dir et de la porte devant le joueur,
        retourner l'information à afficher en continu.
        """
        if self.last_move_dir is None:
            return ""

        # Position ciblée
        new_pos = self.joueur.move(self.last_move_dir)

        # En dehors de la grille
        if not self.manoir.is_inside(new_pos):
            return "There is no door in that direction."

        # Récupérer la pièce actuelle
        current_room = self.manoir.get_piece(self.joueur.position)
        if current_room is None:
            return ""

        # ----- Vérifier SI une porte existe dans cette direction -----
        dir_map = {
            "UP": "N",
            "DOWN": "S",
            "LEFT": "W",
            "RIGHT": "E"
        }
        cardinal = dir_map[self.last_move_dir]

        if not current_room.doors.get(cardinal, False):
            return "There is no door in that direction."

        # ----- Si une pièce existe déjà -----
        if self.manoir.get_piece(new_pos) is not None:
            return ""  # Porte ouverte, passage libre → pas de message

        # ----- Vérifier le verrou -----
        lock_level = self._get_or_create_door_lock(self.joueur.position, new_pos)

        need_key = False
        if lock_level == 1:
            if not self.inventaire.a_objet("lockpick"):
                need_key = True
        elif lock_level == 2:
            need_key = True
            
        # Corridor rule: no lock message
        room_target = self.manoir.get_piece(new_pos)
        if room_target and room_target.nom == "Corridor":
            return ""
        room_current = self.manoir.get_piece(self.joueur.position)
        if room_current and room_current.nom == "Corridor":
            return ""

        if need_key:
            return f"Door locked (level {lock_level}). You need a key or a lockpick."

        return ""


    def can_place_room(self, piece, new_pos):
        """
        Vérifie si une pièce peut être placée à l’emplacement new_pos.
        On vérifie :
        - frontières de la grille
        - correspondance des portes avec toutes les pièces adjacentes
        """

        col, row = new_pos

        # 1) Vérifier limites
        if not self.manoir.is_inside(new_pos):
            return False

        # 2) Vérifier que la case est vide
        if self.manoir.get_piece(new_pos) is not None:
            return False

        # Map des directions cardinales
        dirs = {
            "N": (0, -1),
            "S": (0, 1),
            "E": (1, 0),
            "W": (-1, 0)
        }

        # Pour chaque direction, vérifier compatibilité des portes
        for d, (dx, dy) in dirs.items():
            nx, ny = col + dx, row + dy

            # La pièce voisine
            if not self.manoir.is_inside((nx, ny)):
                continue  # hors grille → pas de contrainte

            neighbor = self.manoir.get_piece((nx, ny))

            if neighbor is None:
                continue  # pas de pièce → aucune contrainte

            # Porte opposée
            opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
            opp = opposite[d]

            # --- Règle fondamentale : portes doivent correspondre ---
            if piece.doors[d] != neighbor.doors[opp]:
                return False

        return True


    def piece_is_placeable(self, piece, player_pos, direction):
        """
        Vérifie si une pièce peut être placée autour du joueur dans la direction donnée.
        - direction : "UP", "DOWN", "LEFT", "RIGHT"
        """

        # --- Conversion direction → coordonnée ---
        dir_to_vec = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
        dx, dy = dir_to_vec[direction]

        target_pos = (player_pos[0] + dx, player_pos[1] + dy)

        # 1) Hors du manoir → impossible
        if not self.manoir.is_inside(target_pos):
            return False

        # 2) La case est déjà occupée → impossible
        if self.manoir.get_piece(target_pos) is not None:
            return False

        # 3) Vérifier compatibilité des portes avec la pièce actuelle
        current_room = self.manoir.get_piece(player_pos)
        if current_room is None:
            return False

        opposite = {"UP": "S", "DOWN": "N", "LEFT": "E", "RIGHT": "W"}
        needed_dir_on_new = opposite[direction]

        # Si la pièce actuelle n'a pas de porte dans cette direction → impossible
        dir_map = {"UP": "N", "DOWN": "S", "LEFT": "W", "RIGHT": "E"}
        if not current_room.doors.get(dir_map[direction], False):
            return False

        # Si la nouvelle pièce n'a pas de porte en face → impossible
        if not piece.doors.get(needed_dir_on_new, False):
            return False

        return True

    # -------------------------------------------------------------
    #   Appliquer les effets spécifiques d'une pièce
    # -------------------------------------------------------------
    def apply_room_effect(self, piece):
        """Applique l'effet spécial de la pièce lorsque le joueur y entre."""

        if piece is None:
            return

        nom = piece.nom
        self.last_effect_message = ""

        # --- Pantry : +4 gold ---
        if nom == "Pantry":
            self.inventaire.gagner_pieces(4)
            self.last_effect_message = "+4 Gold (Pantry)"

        # --- RumpusRoom : +8 gold ---
        elif nom == "RumpusRoom":
            self.inventaire.gagner_pieces(8)
            self.last_effect_message = "+8 Gold (Rumpus Room)"

        # --- Secret_Garden : +20 gold ---
        elif nom == "Secret_Garden":
            self.inventaire.gagner_pieces(20)
            self.last_effect_message = "+20 Gold (Secret Garden)"

        # --- Garage : +3 keys ---
        elif nom == "Garage":
            self.inventaire.gagner_cles(3)
            self.last_effect_message = "+3 Keys (Garage)"

        # --- Nook : +1 key ---
        elif nom == "Nook":
            self.inventaire.gagner_cles(1)
            self.last_effect_message = "+1 Key (Nook)"

        # --- LockerRoom : +5 keys ---
        elif nom == "LockerRoom":
            self.inventaire.gagner_cles(5)
            self.last_effect_message = "+5 Keys (Locker Room)"

        # --- TrophyRoom : +8 diamonds ---
        elif nom == "TrophyRoom":
            self.inventaire.gagner_gemmes(8)
            self.last_effect_message = "+8 Diamonds (Trophy Room)"

        # --- WineCellar : +3 diamonds ---
        elif nom == "WineCellar":
            self.inventaire.gagner_gemmes(3)
            self.last_effect_message = "+3 Diamonds (Wine Cellar)"

        # --- Ballroom : diamonds -> 2 ---
        elif nom == "Ballroom":
            self.inventaire._Inventaire__gemmes = 2
            self.last_effect_message = "Diamonds set to 2 (Ballroom)"

        # --- Walk-in Closet : get 4 random items ---
        elif nom == "Walk-in Closet":
            import random
            gained = []
            for _ in range(4):
                item_name = random.choice(list(self.item_pool.keys()))
                self.add_item_to_inventory(item_name)
                gained.append(item_name)
            self.last_effect_message = "Walk-in Closet: +" + ", ".join(gained)

        # --- Secretpassage : téléportation ---
        elif nom == "Secretpassage":
            self.teleport_to_random_room()
            self.last_effect_message = "Teleported (Secret Passage)"
            
        # --- Kitchen : food shop ---
        elif nom == "Kitchen":
            import random

            foods = ["apple", "carrot", "meat"]
            count = random.randint(1, 5)

            shop_items = random.choices(foods, k=count)

            piece.shop_items = shop_items
            piece.is_shop = True

            from interface import PurchaseItemScreen
            self.game_context.current_screen = PurchaseItemScreen(
                self.game_context, self, self.image_manager, piece
            )

            self.last_effect_message = "Kitchen: food shop opened"





    def add_item_to_inventory(self, name):
        inv = self.inventaire

        # --- Consumables ---
        if name == "coins":
            inv.gagner_pieces(1)
            self.last_effect_message = "You picked up: 1 coin"

        elif name == "gems":
            inv.gagner_gemmes(1)
            self.last_effect_message = "You picked up: 1 gem"

        elif name == "keys":
            inv.gagner_cles(1)
            self.last_effect_message = "You picked up: 1 key"

        elif name == "dice":
            inv.gagner_des(1)
            self.last_effect_message = "You picked up: 1 dice"

        # --- FOOD : auto-use immediately ---
        elif name == "apple":
            steps = self.food_steps["apple"]
            inv.gagner_pas(steps)
            self.last_effect_message = f"You ate an apple (+{steps} steps)"

        elif name == "carrot":
            steps = self.food_steps["carrot"]
            inv.gagner_pas(steps)
            self.last_effect_message = f"You ate a carrot (+{steps} steps)"

        elif name == "meat":
            steps = self.food_steps["meat"]
            inv.gagner_pas(steps)
            self.last_effect_message = f"You ate meat (+{steps} steps)"

        # --- Tools ---
        elif name == "lockpick":
            inv.gagner_lockpick()
            self.last_effect_message = "You picked up: lockpick"

        elif name == "rabbit_foot":
            inv.gagner_rabbit_foot()
            self.last_effect_message = "You picked up: rabbit foot"

        elif name == "metal_detector":
            inv.gagner_metal_detector()
            self.last_effect_message = "You picked up: metal detector"


    def reroll_room_choices(self):
        """
        Utilisé lorsque le joueur appuie sur R dans l'écran RoomChoice.
        Dépense un dé et génère un nouveau tirage de 3 pièces.
        """
        # Vérifier si le joueur a au moins 1 dé
        if self.inventaire.des <= 0:
            return None, "You have no dice to reroll."

        # Dépenser un dé
        self.inventaire.depenser_des(1)

        # Refaire exactement la même logique que try_open_door()
        direction = self.last_move_dir
        player_pos = self.joueur.position

        # Cherche toutes les variantes jouables (0, 90°, 180°, 270°)
        def get_valid_rotation(template):
            p = template.clone()
            for _ in range(4):
                if self.piece_is_placeable(p, player_pos, direction):
                    return p
                p.rotate_90()
            return None

        playable = []
        for templ in self.catalogue:
            fixed = get_valid_rotation(templ)
            if fixed:
                playable.append(fixed)

        if not playable:
            return None, "No possible room can be placed."

        playable_free = [p for p in playable if p.gem_cost == 0]
        if not playable_free:
            return None, "No free room available."

        import random
        r1 = random.choice(playable_free)
        others = [p for p in playable if p.nom != r1.nom]

        if len(others) >= 2:
            r2, r3 = random.sample(others, 2)
        else:
            r2 = others[0]
            r3 = random.choice(playable_free)

        room_options = [r1, r2, r3]
        random.shuffle(room_options)

        return room_options, "Rerolled using 1 die."
