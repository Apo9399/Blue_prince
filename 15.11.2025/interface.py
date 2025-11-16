#interface.py
import pygame
from abc import ABC, abstractmethod

class ImageManager:
    """
    Charge et met en cache les images du jeu pour optimiser les performances.
    """
    def __init__(self, asset_folder="assets/"):
        self.asset_folder = asset_folder
        self.cache = {}

    def load(self, filename, scale=None, rotate=0):
        """
        Charge une image depuis le dossier assets.
        Si 'scale' (tuple (width, height)) est fourni, redimensionne l'image.
        """
        path = f"{self.asset_folder}{filename}"
        
        ### CORRECTION ### 
        # Une clé de cache qui gère le redimensionnement
        cache_key = path
        if scale:
            cache_key = f"{path}_{scale[0]}x{scale[1]}_rot{rotate}"
        else:
            cache_key = f"{path}_rot{rotate}"


        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            image = pygame.image.load(path)
            if rotate != 0:
                image = pygame.transform.rotate(image, -rotate)
            if scale:
                image = pygame.transform.scale(image, scale)
            
            image = image.convert_alpha()
            self.cache[cache_key] = image # Met la bonne image dans le cache
            return image # Retourne la nouvelle image
        
        except FileNotFoundError:
            print(f"Erreur: Impossible de charger l'image {path}")
            error_surface = pygame.Surface(scale if scale else (50, 50)) # Adapte la taille du carré
            error_surface.fill((255, 0, 0))
            return error_surface
        ### CORRECTION ### Ajout d'une capture d'erreur plus large
        except Exception as e:
            print(f"Erreur (pas FileNotFoundError) pour {path}: {e}")
            error_surface = pygame.Surface(scale if scale else (50, 50))
            error_surface.fill((255, 0, 0))
            return error_surface

class AbstractScreen(ABC):
    """
    Classe de base abstraite pour les différents écrans du jeu.
    """
    def __init__(self, game_context):
        self.game = game_context

    @abstractmethod
    def handle_input(self, event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self, surface):
        pass

class GrilleAffiche:
    """
    Affiche la grille du manoir 5x9 et la position du joueur.
    """
    def __init__(self, game_logic, image_manager):
        self.game_logic = game_logic 
        self.image_manager = image_manager
        self.tile_size = 64
        self.grid_pos = (50, 50)

    def draw(self, surface):
        """
        Dessine la grille, les pièces découvertes, et le curseur du joueur.
        """
        for y in range(self.game_logic.manoir.rows):
            for x in range(self.game_logic.manoir.cols):
                rect = (self.grid_pos[0] + x * self.tile_size,
                        self.grid_pos[1] + y * self.tile_size,
                        self.tile_size, self.tile_size)

                piece = self.game_logic.manoir.get_piece((x, y))

                if piece:
                    try:
                        piece_img = self.image_manager.load(
                                                        piece.image_name,
                                                        (self.tile_size, self.tile_size),
                                                        rotate=piece.rotation
                                                    )

                        # --- C'EST LA LIGNE CORRIGÉE ---
                        # On passe (rect[0], rect[1]) qui sont les coords (x, y)
                        surface.blit(piece_img, (rect[0], rect[1])) 
                        # L'ancienne ligne était: surface.blit(piece_img, rect.topleft)
                        
                    except Exception as e:
                        # Cette erreur s'affiche maintenant dans la console
                        print(f"Erreur chargement image pièce {piece.image_name}: {e}")
                        pygame.draw.rect(surface, (255, 0, 255), rect)
                else:
                    pygame.draw.rect(surface, (10, 10, 10), rect)
                
                pygame.draw.rect(surface, (40, 40, 40), rect, 1)

        # 4. Dessiner le "curseur" sur la pièce du joueur
        player_pos = self.game_logic.get_player_position() # (col, ligne)
        player_rect = (self.grid_pos[0] + player_pos[0] * self.tile_size, 
                         self.grid_pos[1] + player_pos[1] * self.tile_size, 
                         self.tile_size, 
                         self.tile_size)
        pygame.draw.rect(surface, (255, 255, 0), player_rect, 3) # Curseur jaune
        
        
        # --- Direction Indicator (white diamond) ---
        direction = self.game_logic.last_move_dir
        if direction:
            cx = player_rect[0] + self.tile_size // 2   # center X
            cy = player_rect[1] + self.tile_size // 2   # center Y
            offset = self.tile_size // 2 + 6            # distance from center

            if direction == "UP":
                points = [
                    (cx, cy - offset),  # top
                    (cx - 8, cy - offset + 8),
                    (cx, cy - offset + 16),
                    (cx + 8, cy - offset + 8)
                ]
            elif direction == "DOWN":
                points = [
                    (cx, cy + offset),  # bottom
                    (cx - 8, cy + offset - 8),
                    (cx, cy + offset - 16),
                    (cx + 8, cy + offset - 8)
                ]
            elif direction == "LEFT":
                points = [
                    (cx - offset, cy),  # left
                    (cx - offset + 8, cy - 8),
                    (cx - offset + 16, cy),
                    (cx - offset + 8, cy + 8)
                ]
            elif direction == "RIGHT":
                points = [
                    (cx + offset, cy),  # right
                    (cx + offset - 8, cy - 8),
                    (cx + offset - 16, cy),
                    (cx + offset - 8, cy + 8)
                ]

            pygame.draw.polygon(surface, (255, 255, 255), points)

class AfficheInventaire:
    """
    Gère l'affichage des ressources et objets de l'inventaire.
    """
    def __init__(self, game_logic, image_manager):
        self.game_logic = game_logic
        self.image_manager = image_manager
        self.font = pygame.font.Font(None, 28) 
        
        icon_size = (32, 32)
        
        ### CORRECTION ###
        # J'ai standardisé les noms : minuscules et sans accents
        # pour correspondre à RoomChoiceScreen et éviter les carrés rouges.
        # Assure-toi que tes fichiers s'appellent :
        # "icon_pas.png", "icon_or.png", "icon_gemme.png", "icon_cle.png", "icon_des.png"
        self.icons = {
            "pas": self.image_manager.load("icon_pas.png", icon_size),
            "or": self.image_manager.load("icon_or.png", icon_size),
            "gemme": self.image_manager.load("icon_gemme.png", icon_size),
            "cle": self.image_manager.load("icon_cle.png", icon_size),
            "des": self.image_manager.load("icon_des.png", icon_size),
        }
        
    def draw(self, surface, pos): 
        """
        Affiche les ressources verticalement à partir de la position (x, y) donnée.
        """
        x_start, y_start = pos
        y_offset = 0
        icon_padding = 40
        text_color = (0, 0, 0)

        # 1. Pas
        pas = self.game_logic.get_steps()
        surface.blit(self.icons["pas"], (x_start, y_start + y_offset))
        text_pas = self.font.render(str(pas), True, text_color)
        surface.blit(text_pas, (x_start + 40, y_start + y_offset + 8))
        y_offset += icon_padding

        # 2. Or
        or_ = self.game_logic.get_gold()
        surface.blit(self.icons["or"], (x_start, y_start + y_offset))
        text_or = self.font.render(str(or_), True, text_color)
        surface.blit(text_or, (x_start + 40, y_start + y_offset + 8))
        y_offset += icon_padding

        # 3. Gemmes
        gemmes = self.game_logic.get_gems()
        surface.blit(self.icons["gemme"], (x_start, y_start + y_offset))
        text_gemmes = self.font.render(str(gemmes), True, text_color)
        surface.blit(text_gemmes, (x_start + 40, y_start + y_offset + 8))
        y_offset += icon_padding

        # 4. Clés
        cles = self.game_logic.get_keys()
        surface.blit(self.icons["cle"], (x_start, y_start + y_offset))
        text_cles = self.font.render(str(cles), True, text_color)
        surface.blit(text_cles, (x_start + 40, y_start + y_offset + 8))
        y_offset += icon_padding
        
        # 5. Dés
        des = self.game_logic.get_dice()
        surface.blit(self.icons["des"], (x_start, y_start + y_offset))
        text_des = self.font.render(str(des), True, text_color)
        surface.blit(text_des, (x_start + 40, y_start + y_offset + 8))

class GameScreen(AbstractScreen):
    """
    Écran de jeu principal. Contient la grille et l'inventaire.
    """
    def __init__(self, game_context, game_logic, image_manager):
        super().__init__(game_context)
        self.grille_view = GrilleAffiche(game_logic, image_manager)
        self.inventory_view = AfficheInventaire(game_logic, image_manager)
        self.game_logic = game_logic
        self.title_font = pygame.font.Font(None, 36)
        self.message = ""
        
        # --- Définition des zones ---
        self.GRID_ZONE_WIDTH = 420 
        self.PANEL_START_X = 420   
        
        ### CORRECTION ### (C'est la 2ème ligne que tu voulais changer)
        # J'ai élargi le panneau blanc de 400 à 550 pour voir les 3 salles
        self.PANEL_WIDTH = 550   # <-- MODIFIÉ (de 400)
        
        self.PANEL_COLOR = (230, 230, 230)
        self.BACKGROUND_COLOR = (20, 20, 20) 
        self.TEXT_COLOR = (0, 0, 0) 

    def handle_input(self, event):
        """
        Gère les déplacements (ZQSD) et l'ouverture de porte (Espace).
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z: # Haut
                self.game_logic.move_player("UP")
            elif event.key == pygame.K_s: # Bas
                self.game_logic.move_player("DOWN")
            elif event.key == pygame.K_q: # Gauche
                self.game_logic.move_player("LEFT")
            elif event.key == pygame.K_d: # Droite
                self.game_logic.move_player("RIGHT")
            elif event.key == pygame.K_SPACE: # Valider
                result = self.game_logic.try_open_door()
                #s'il y a un message, afficher le
                if result.message:
                    self.message = result.message
                if result.needs_room_choice:
                    self.game.show_room_choice(result.room_options)

    def update(self):
        pass

    def draw(self, surface):
        grid_background_rect = (0, 0, self.GRID_ZONE_WIDTH, surface.get_height())
        surface.fill(self.BACKGROUND_COLOR, rect=grid_background_rect)

        inventory_panel_rect = (self.PANEL_START_X, 0, self.PANEL_WIDTH, surface.get_height())
        pygame.draw.rect(surface, self.PANEL_COLOR, inventory_panel_rect)

        self.grille_view.draw(surface) 

        # inventaire name
        inv_title = self.title_font.render("Inventory:", True, self.TEXT_COLOR)
        surface.blit(inv_title, (self.PANEL_START_X + 20, 50)) 
        
        self.inventory_view.draw(surface, (self.PANEL_START_X + 20, 100))
        
        # room name
        player_pos = self.game_logic.get_player_position()
        current_room = self.game_logic.manoir.get_piece(player_pos)

        if current_room:
            room_title = self.title_font.render(current_room.nom, True, (0, 0, 0))
            surface.blit(room_title, (self.PANEL_START_X + 20, 350))

        
        msg = self.game_logic.get_current_door_message()
        if msg:
            font = self.game.font_small
            text = font.render(msg, True, (0, 0, 0))
            surface.blit(text, (self.PANEL_START_X + 20, 740))

class RoomChoiceScreen(AbstractScreen):
    """
    Écran de sélection de pièce, style 'Blue Prince'.
    """
    def __init__(self, game_context, game_logic, image_manager, room_options):
        super().__init__(game_context)
        self.game_logic = game_logic
        self.image_manager = image_manager
        self.room_options = room_options 
        self.selected_index = 0 

 
        # CORRECTION:
        # Ajouter : créer un **GameScreen** pour dessiner la grille de gauche.
        self.game_screen = GameScreen(game_context, game_logic, image_manager)
        
        # Polices
        self.title_font = pygame.font.Font(None, 36)
        self.room_font = pygame.font.Font(None, 28)
        self.text_font = pygame.font.Font(None, 24)
        
        # Composant Inventaire
        self.inventory_view = AfficheInventaire(game_logic, image_manager)
        
        # Icônes (Noms standardisés)
        self.gem_icon = self.image_manager.load("icon_gemme.png", (20, 20))
        self.dice_icon = self.image_manager.load("icon_des.png", (20, 20))
        
        # --- Définition des zones et couleurs ---
        self.PANEL_START_X = 420   
        self.GRID_ZONE_WIDTH = 420 
        
        self.COLOR_WHITE_PANEL = (230, 230, 230)
        self.COLOR_BACKGROUND = (0, 0, 0)
        self.COLOR_TEXT = (0, 0, 0)
        self.COLOR_HIGHLIGHT = (0, 150, 255) 
        
        
        ############################################################
        #      ROTATION AUTOMATIQUE DES 3 SALLES PROPOSÉES        #
        ############################################################

        # --- 1) Récupérer la direction du déplacement ---
        # Cette direction indique où la nouvelle salle doit être placée
        dir_map = {
            "UP":    "N",
            "DOWN":  "S",
            "LEFT":  "W",
            "RIGHT": "E"
        }

        # Si aucune direction, pas de rotation possible
        if self.game_logic.last_move_dir is None:
            return


        # Direction cardinal du déplacement (ex: "W")
        placement_dir = dir_map[self.game_logic.last_move_dir]
        print(placement_dir)

        # Direction opposée (porte requise sur la nouvelle salle)
        opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
        needed_on_new = opposite[placement_dir]     # ex: si W → new doit avoir porte E
        needed_on_current = placement_dir           # pièce actuelle doit avoir porte W

        # --- 2) Récupérer la pièce actuelle ---
        current_pos = self.game_logic.get_player_position()
        current_room = self.game_logic.manoir.get_piece(current_pos)

        if current_room is None:
            print("Erreur : pièce courante introuvable !")
            return

        # --- 3) Vérifier si la pièce actuelle possède une porte dans la bonne direction ---
        if not current_room.doors.get(needed_on_current, False):
            # Le joueur ne devrait même pas pouvoir bouger ici
            print("Avertissement : la salle actuelle n’a pas de porte dans cette direction.")
            return

        # --- 4) Rotation automatique des 3 salles proposées ---
        for piece in self.room_options:

            # Tester jusqu'à 4 rotations (0°, 90°, 180°, 270°)
            for _ in range(4):

                # Condition correcte :
                # condition 1 : la nouvelle pièce a une porte du bon côté
                cond1 = piece.doors.get(needed_on_new, False)

                if cond1:
                    break

                # Sinon → rotation 90°
                piece.rotate_90()

    def handle_input(self, event):
        """
        Gère la sélection (Gauche/Droite) et la validation (Entrée).
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_q:
                self.selected_index = (self.selected_index - 1) % len(self.room_options)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.selected_index = (self.selected_index + 1) % len(self.room_options)
            elif event.key == pygame.K_RETURN: # Touche "Entrée"
                chosen_room = self.room_options[self.selected_index]
                if self.game_logic.select_room(chosen_room):
                    self.game.show_game_screen()
                else:
                    print("Pas assez de gemmes !")

    def update(self):
        pass

    def draw(self, surface):
        grid_background_rect = (0, 0, self.GRID_ZONE_WIDTH, surface.get_height())
        surface.fill(self.COLOR_BACKGROUND, rect=grid_background_rect)
        
        #CORRECTION:
        #Dessiner la grille du manoir située à gauche.
        self.game_screen.grille_view.draw(surface)

        
        panel_width = surface.get_width() - self.GRID_ZONE_WIDTH
        panel_rect = (self.PANEL_START_X, 0, panel_width, surface.get_height())
        pygame.draw.rect(surface, self.COLOR_WHITE_PANEL, panel_rect)

        inv_title = self.title_font.render("Inventory:", True, self.COLOR_TEXT)
        surface.blit(inv_title, (self.PANEL_START_X + 20, 50)) 
        self.inventory_view.draw(surface, (self.PANEL_START_X + 20, 100))
        
        player_pos = self.game_logic.get_player_position()
        current_room = self.game_logic.manoir.get_piece(player_pos)

        draft_title = self.title_font.render("Choose a room to draft", True, self.COLOR_TEXT)
        surface.blit(draft_title, (self.PANEL_START_X + 20, 350)) 

        room_size = (150, 150)
        start_x_rooms = self.PANEL_START_X + 20 
        start_y_rooms = 400
        spacing = 180 

        for i, room in enumerate(self.room_options):
            x_pos = start_x_rooms + i * spacing 
            
            room_img = self.image_manager.load(room.image_name, room_size, rotate=room.rotation)
            surface.blit(room_img, (x_pos, start_y_rooms))
            
            room_name_text = self.room_font.render(room.nom, True, self.COLOR_TEXT)
            text_rect = room_name_text.get_rect(center=(x_pos + room_size[0] // 2, start_y_rooms + room_size[1] + 20))
            surface.blit(room_name_text, text_rect)

            # --- C'EST LA LIGNE CORRIGÉE ---
            # J'ai remplacé self.font par self.room_font
            cost_text = self.room_font.render(str(room.gem_cost), True, self.COLOR_TEXT)
            cost_x_pos = x_pos + (room_size[0] // 2)
            surface.blit(self.gem_icon, (cost_x_pos - 15, start_y_rooms + room_size[1] + 40))
            surface.blit(cost_text, (cost_x_pos + 10, start_y_rooms + room_size[1] + 38))

            if i == self.selected_index:
                highlight_rect = (x_pos - 5, start_y_rooms - 5, room_size[0] + 10, room_size[1] + 70)
                pygame.draw.rect(surface, self.COLOR_HIGHLIGHT, highlight_rect, 4)
                
                room_name_text_sel = self.room_font.render(room.nom, True, self.COLOR_HIGHLIGHT)
                surface.blit(room_name_text_sel, text_rect)

        redraw_title = self.title_font.render("Redraw", True, self.COLOR_TEXT)
        surface.blit(redraw_title, (self.PANEL_START_X + 20, 650)) 
        
        redraw_text = self.text_font.render("with dice", True, (100, 100, 100)) 
        surface.blit(redraw_text, (self.PANEL_START_X + 20, 690)) 
        surface.blit(self.dice_icon, (self.PANEL_START_X + 20 + redraw_text.get_width() + 5, 688))