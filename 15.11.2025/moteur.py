# moteur.py
import random
from inventaire import Inventaire


# ─────────────────────────────────────────────
# Données simples utilisés pour simuler des pièces
# ─────────────────────────────────────────────

class Piece:
    """Représente une pièce simple du manoir."""

    def __init__(self, nom, image_name, gem_cost, doors):
        self.nom = nom
        self.image_name = image_name
        self.gem_cost = gem_cost
        
        # doors par exemple : {"N": True, "S": False, "E": True, "W": False}
        self.doors = doors  

        # Angle de rotation actuel (utilisé pour la rotation de l’image).
        self.rotation = 0

    def rotate_90(self):
        """
        Faire pivoter de 90° dans le sens horaire 
        et mettre à jour l‘orientation des portes.
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
        new = Piece(self.nom, self.image_name, self.gem_cost, self.doors.copy())
        new.rotation = self.rotation   # ← 必须加
        return new


# ─────────────────────────────────────────────
# Manoir = grille (5 colonnes × 9 lignes)
# ─────────────────────────────────────────────

class Manoir:
    def __init__(self, rows=9, cols=5):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]

    def get_piece(self, pos):
        col, row = pos
        return self.grid[row][col]

    def set_piece(self, pos, piece):
        col, row = pos
        self.grid[row][col] = piece

    def is_inside(self, pos):
        col, row = pos
        return 0 <= col < self.cols and 0 <= row < self.rows


# ─────────────────────────────────────────────
# Joueur
# ─────────────────────────────────────────────

class Joueur:
    def __init__(self, start_position):
        self.position = start_position  # tuple (col, row)

    def move(self, direction):
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
    def __init__(self, needs_room_choice=False, room_options=None,message=""):
        self.needs_room_choice = needs_room_choice
        self.room_options = room_options or []
        self.message = message 

# ─────────────────────────────────────────────
# GameLogic (le moteur)
# ─────────────────────────────────────────────

class GameLogic:
    def __init__(self):
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

        # 2. Créer le catalogue de pièces à tirer
        # (Chemins simples, car les images sont DANS assets/)
        self.catalogue = [
            # Salles Bleues
            Piece("Pantry",         "Pantry_Icon.png",            0, {"N":False, "S":True,  "E":False,  "W":True}),  # cuisine-garde-manger, deux portes adjacentes
            Piece("Walk-in Closet", "Walk-in_Closet_Icon.png",    1, {"N":False, "S":True, "E":False,  "W":False }),  # dressing, deux portes opposées gauche/droite
            Piece("Ballroom",       "Ballroom_Icon.png",          1, {"N":True,  "S":True,  "E":False, "W":False}),  # grande salle, deux portes nord/sud
            Piece("Billiard_room",  "Billiard_Room_Icon.png",     1, {"N":False, "S":True,  "E":False,  "W":True}),  # billard, deux portes adjacentes
            Piece("Aquarium",       "Aquarium_Icon.png",          3, {"N":False,  "S":True,  "E":True,  "W":True}),  # aquarium, trois portes (T-forme)
            Piece("DiningRoom",     "Dining_Room_Icon.png",       1, {"N":False,  "S":True, "E":True,  "W":True}),  # salle à manger, deux portes adjacentes
            Piece("Gallery",        "Gallery_Icon.png",           1, {"N":True, "S":True,  "E":False,  "W":False}),  # galerie, trois portes (T-forme)
            Piece("Garage",         "Garage_Icon.png",            1, {"N":False, "S":True,  "E":False, "W":False}),  # garage, deux portes adjacentes
            Piece("LockerRoom",     "Locker_Room_Icon.png",       0, {"N":True,  "S":True, "E":False,  "W":False}),  # vestiaire, deux portes adjacentes
            Piece("Nook",           "Nook_Icon.png",              0, {"N":False, "S":True,  "E":False,  "W":True}),  # alcôve, deux portes adjacentes
            Piece("Room8",          "Room_8_Icon.png",            0, {"N":False,  "S":True,  "E":False, "W":True}),  # Room8, deux portes nord/sud
            Piece("RumpusRoom",     "Rumpus_Room_Icon.png",       0, {"N":True, "S":True,  "E":False,  "W":False}),  # salle de jeux, deux portes adjacentes
            Piece("TrophyRoom",     "Trophy_Room_Icon.png",       0, {"N":False,  "S":True, "E":False,  "W":True}),  # salle des trophées, deux portes adjacentes
            Piece("WineCellar",     "Wine_Cellar_Icon.png",       1, {"N":False,  "S":True, "E":False, "W":False }),  # cave à vin, deux portes adjacentes

            # Salles Vertes
            Piece("Secret_Garden",  "Secret_Garden_Icon.png",     1, {"N":False,  "S":True,  "E":True, "W":True }),  # jardin secret, trois portes
            Piece("Veranda",        "Veranda_Icon.png",           2, {"N":True, "S":True,  "E":False,  "W":False}),  # véranda, deux portes adjacentes

            # Salles Dorées
            Piece("Kitchen",        "Kitchen_Icon.png",           2, {"N":False,  "S":True,  "E":False, "W":True}),  # cuisine, deux portes nord/sud
            Piece("Showroom",       "Showroom_Icon.png",          3, {"N":True, "S":True,  "E":False,  "W":False}),  # showroom, deux portes adjacentes

            # Salles Violet
            Piece("BunkRoom",       "Bunk_Room_Icon.png",         0, {"N":False,  "S":True, "E":False,  "W":False}),  # chambre bunk, deux portes adjacentes
            Piece("LadyChamber",    "Her_Ladyship's_Chamber_Icon.png", 0, {"N":False,  "S":True,  "E":False, "W":False}),  # chambre de dame, deux portes nord/sud

            # Salles Orange
            Piece("Corridor",       "Corridor_Icon.png",          0, {"N":True,  "S":True,  "E":False, "W":False}),  # couloir, deux portes nord/sud (corridor type)
            Piece("EastWingHall",   "East_Wing_Hall_Icon.png",    0, {"N":False,  "S":True, "E":True,  "W":True }),  # hall aile est, trois portes
            Piece("GreatHall",      "Great_Hall_Icon.png",        0, {"N":True,  "S":True,  "E":True,  "W":True }),  # grande salle, quatre portes
            Piece("Passageway",     "Passageway_Icon.png",        0, {"N":True,  "S":True,  "E":True,  "W":True}),  # passage, trois portes
            Piece("Secretpassage",  "Secret_Passage_Icon.png",    0, {"N":False, "S":True,  "E":False,  "W":False })  # passage secret, trois portes
        ]


        # Memoire de la direction
        self.last_move_dir = None
        
        # Etat du jeu
        self.game_over = False
        self.player_won = False
        
        #la porte
        self.doors = {}

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
        self.last_move_dir = direction  # Enregistre la direction visée

        new_pos = self.joueur.move(direction)

        # 1. Vérifie si la case est dans la grille
        if not self.manoir.is_inside(new_pos):
            return

        # 2. Vérifie si une pièce existe DÉJÀ
        if self.manoir.get_piece(new_pos) is not None:
            self.joueur.position = new_pos
            self.inventaire.perdre_pas()
            
            #verifie la condition de fini apres le mouvement
            self.check_end_conditions()
            return

        # 3. Si la case est vide (None)
        # Le joueur ne bouge PAS.
        # Le jeu attend que le joueur appuie sur ESPACE.
        
        pass

    # ────────────────────────────────
    # Tentative d’ouvrir une porte → tirage des 3 pièces
    # ────────────────────────────────
    def try_open_door(self):
        
        # Sécurité: Ne fait rien si le joueur n'a pas visé une direction
        if self.last_move_dir is None:
            return TryOpenDoorResult(needs_room_choice=False)
            
        # Sécurité: Vérifie si la case visée est valide
        new_pos = self.joueur.move(self.last_move_dir)
        if not self.manoir.is_inside(new_pos):
            self.last_move_dir = None # Réinitialise la direction
            return TryOpenDoorResult(needs_room_choice=False)
            
        # Sécurité: Vérifie si la case n'est pas déjà prise
        if self.manoir.get_piece(new_pos) is not None:
            self.last_move_dir = None # Réinitialise la direction
            return TryOpenDoorResult(needs_room_choice=False)


        # Vérifier/générer le niveau du verrou de la porte.
        lock_level = self._get_or_create_door_lock(self.joueur.position, new_pos)

        # Logique des clés / outils de déverrouillage.
        need_key = False
        if lock_level == 0:
            need_key = False
        elif lock_level == 1:
            # Avec un crochet de serrure (Lockpick), il est possible de ne pas consommer de clé.
            if not self.inventaire.a_objet("Lockpick"):
                need_key = True
        elif lock_level == 2:
            # Un verrou de niveau 2 doit obligatoirement être ouvert avec une clé.
            need_key = True

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

        
        
        # Si tout est bon, on tire 3 pièces
        room_templates = random.sample(self.catalogue, 3)
        room_options = [room.clone() for room in room_templates]


        # Retourne un objet que interface.py peut interpréter
        return TryOpenDoorResult(
            needs_room_choice=True,
            room_options=room_options
        )

    # ────────────────────────────────
    # Choix d’une pièce dans l’écran RoomChoice
    # ────────────────────────────────
    def select_room(self, piece):
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

        # 3. Place la pièce dans la grille
        self.manoir.set_piece(new_pos, piece)

        # 4. Déplace le joueur dans la nouvelle pièce
        self.joueur.position = new_pos

        # 5. Dépense un "pas"
        self.inventaire.perdre_pas()
        
        # 6. Réinitialise la direction
        self.last_move_dir = None
        
        # 7. Placer une nouvelle pièce et vérifier la victoire après y être entré.
        self.check_end_conditions()
        
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


    # ────────────────────────────────
    # Creer le verrou
    # ────────────────────────────────
    
    def _get_or_create_door_lock(self, from_pos, to_pos):
        """
        Retourner le niveau de verrou de la porte entre les deux cases.
        S'il n'existe pas encore de verrou pour cette arête, en créer un aléatoirement selon les règles de ligne :

        - Dans les deux lignes les plus basses (lignes 7 et 8), uniquement des verrous de niveau 0
        - Dans les deux lignes supérieures (lignes 0 et 1), uniquement des verrous de niveau 2
        - Dans les autres lignes, niveau 0/1/2 aléatoire (avec une légère préférence pour 1)
        """
        key = frozenset({from_pos, to_pos})
        if key in self.doors:
            return self.doors[key]

        _, row_from = from_pos
        _, row_to = to_pos
        min_row = min(row_from, row_to)

        if min_row >= 5:
            lock_level = 0
        elif min_row <= 1:
            lock_level = 2
        else:
            # middle zone: prefer to have a lock 1
            lock_level = random.choice([0, 1, 1, 1, 2])

        self.doors[key] = lock_level
        return lock_level
    
    

    def get_current_door_message(self):
        """
        Pour l'interface : en fonction de last_move_dir et de la porte devant le joueur, retourner l'information à afficher en continu.
        """
        if self.last_move_dir is None:
            return ""

        new_pos = self.joueur.move(self.last_move_dir)
        if not self.manoir.is_inside(new_pos):
            return ""

        if self.manoir.get_piece(new_pos) is not None:
            return ""

        lock_level = self._get_or_create_door_lock(self.joueur.position, new_pos)

        need_key = False
        if lock_level == 0:
            need_key = False
        elif lock_level == 1:
            if not self.inventaire.a_objet("Lockpick"):
                need_key = True
        elif lock_level == 2:
            need_key = True

        if need_key:
            return f"Door locked (level {lock_level}). You need a key or a lockpick."

        return ""
