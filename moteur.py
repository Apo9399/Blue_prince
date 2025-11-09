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

        # Créer pièce de départ
        start_room = Piece("Entrée", "entrance.png", 0)
        self.manoir.set_piece(self.joueur.position, start_room)

        start_room = Piece("Entrée", "salles/speciale/entree.png", 0) # <--- CETTE LIGNE
        self.manoir.set_piece(self.joueur.position, start_room)

        # 2. Créer le catalogue de pièces à tirer
        # Mettez ici les chemins vers vos images "par couleur"
        self.catalogue = [                                          # <--- ET CELLES-CI
            # Salles Bleues
            Piece("Pantry", "salles/bleu/pantry.png", 0),
            Piece("Walk-in Closet", "salles/bleu/walk_in_closet.png", 1),
            Piece("Salle de Bain", "salles/bleu/salle_de_bain.png", 1),
            
            # Salles Vertes
            Piece("Kitchen", "salles/vert/kitchen.png", 1),
            Piece("Serre", "salles/vert/serre.png", 2),
            
            # Salles Dorées
            Piece("Salle Dorée", "salles/or/salle_doree.png", 2),
            Piece("Bibliothèque", "salles/or/bibliotheque.png", 3),
            
            # ... ajoutez toutes vos autres pièces ici
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
        self.last_move_dir = direction  # ✅ 记录方向

        new_pos = self.joueur.move(direction)

        # 不在地图内 → 无效移动
        if not self.manoir.is_inside(new_pos):
            return

        # 已有房间 → 直接进入
        if self.manoir.get_piece(new_pos) is not None:
            self.joueur.position = new_pos
            self.inventaire.perdre_pas()
            return

        # 到这里就是需要开新房间的情况
        # 不移动玩家，此时等待 SPACE / 房间选择界面

    # ────────────────────────────────
    # Tentative d’ouvrir une porte → tirage des 3 pièces
    # ────────────────────────────────
    def try_open_door(self):
        # Tirage aléatoire de 3 pièces (simplifié)
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
        # 扣宝石
        if not self.inventaire.depenser_gemmes(piece.gem_cost):
            return False

        col, row = self.joueur.position

        # ✅ 根据最后移动方向决定新房间坐标
        if self.last_move_dir == "UP":
            new_pos = (col, row - 1)
        elif self.last_move_dir == "DOWN":
            new_pos = (col, row + 1)
        elif self.last_move_dir == "LEFT":
            new_pos = (col - 1, row)
        elif self.last_move_dir == "RIGHT":
            new_pos = (col + 1, row)
        else:
            return False  # 理论上不可能，但保底

        # ✅ 放置房间
        self.manoir.set_piece(new_pos, piece)

        # ✅ 把玩家移到新房间
        self.joueur.position = new_pos

        # ✅ 消耗步数
        self.inventaire.perdre_pas()

        return True


