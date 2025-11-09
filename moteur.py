# moteur.py
import random
from inventaire import Inventaire


# ─────────────────────────────────────────────
# Données simples utilisés pour simuler des pièces
# ─────────────────────────────────────────────

class Piece:
    """Représente une pièce simple du manoir."""

    def __init__(self, nom, image_name, gem_cost=0):
        self.nom = nom
        self.image_name = image_name
        self.gem_cost = gem_cost


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
    def __init__(self, needs_room_choice=False, room_options=None):
        self.needs_room_choice = needs_room_choice
        self.room_options = room_options or []


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
        start_room = Piece("Entrée", "Entrance_Hall_Icon.png", 0)
        self.manoir.set_piece(self.joueur.position, start_room)

        # 2. Créer le catalogue de pièces à tirer
        # (Chemins simples, car les images sont DANS assets/)
        self.catalogue = [
            # Salles Bleues
            Piece("Pantry", "Pantry_Icon.png", 0),
            Piece("Walk-in Closet", "Walk-in_Closet_Icon.png", 1),
            Piece("Ballroom", "Ballroom_Icon.png", 1),
            Piece("Billiard_room", "Billiard_Room_Icon.png", 1),
            Piece("Aquarium", "Aquarium_Icon.png", 3),
            Piece("DinningRoom", "Dining_Room_Icon.png", 1),
            Piece("Gallery", "Gallery_Icon.png", 1),
            Piece("Garage", "Garage_Icon.png", 1),
            Piece("LockerRoom", "Locker_Room_Icon.png", 0),
            Piece("Nook", "Nook_Icon.png", 0),
            Piece("Room8", "Room_8_Icon.png", 0),
            Piece("RumpusRoom", "Rumpus_Room_Icon.png", 0),
            Piece("TrophyRoom", "Trophy_Room_Icon.png", 0),
            Piece("WineCellar", "Wine_Cellar_Icon.png", 1),
            
            # Salles Vertes
            Piece("Secret_Garden", "Secret_Garden_Icon.png", 1),
            Piece("Veranda", "Veranda_Icon.png", 2),
            
            # Salles Dorées
            Piece("Kitchen", "Kitchen_Icon.png", 2),
            Piece("Showroom", "Showroom_Icon.png", 3),
            
            # Salles Violet
            Piece("BunkRoom", "Bunk_Room_Icon.png", 0),
            Piece("LadyChamber", "Her_Ladyship's_Chamber_Icon.png", 0),
            
            # Salles orange
            Piece("Corridor", "Corridor_Icon.png", 0),
            Piece("EastWingHall", "East_Wing_Hall_Icon.png", 0),
            Piece("GreatHall", "Great_Hall_Icon.png", 0),
            Piece("Passageway", "Passageway_Icon.png", 0),
            Piece("Secretpassage", "Secret_Passage_Icon.png", 0),
        ]

        self.last_move_dir = None

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
        self.last_move_dir = direction  # ✅ Enregistre la direction visée

        new_pos = self.joueur.move(direction)

        # 1. Vérifie si la case est dans la grille
        if not self.manoir.is_inside(new_pos):
            return

        # 2. Vérifie si une pièce existe DÉJÀ
        if self.manoir.get_piece(new_pos) is not None:
            self.joueur.position = new_pos
            self.inventaire.perdre_pas()
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

        # Si tout est bon, on tire 3 pièces
        room_options = random.sample(self.catalogue, 3)

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

        return True
