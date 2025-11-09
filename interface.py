import pygame
from abc import ABC, abstractmethod

class ImageManager:
    """
    Charge et met en cache les images du jeu pour optimiser les performances.
    Les images sont récupérées sur le wiki comme suggéré.
    """
    def __init__(self, asset_folder="assets/"):
        self.asset_folder = asset_folder
        self.cache = {}

    def load(self, filename, scale=None):
        """
        Charge une image depuis le dossier assets.
        Si 'scale' (tuple (width, height)) est fourni, redimensionne l'image.
        """
        path = f"{self.asset_folder}{filename}"
        if path in self.cache:
            return self.cache[path]
        
        try:
            image = pygame.image.load(path)
            if scale:
                image = pygame.transform.scale(image, scale)
            
            # Utiliser convert_alpha() est crucial pour la transparence et les performances
            self.cache[path] = image.convert_alpha()
            return self.cache[path]
        except FileNotFoundError:
            print(f"Erreur: Impossible de charger l'image {path}")
            # Retourner une surface rouge pour visualiser l'erreur
            error_surface = pygame.Surface((50, 50))
            error_surface.fill((255, 0, 0))
            return error_surface

class AbstractScreen(ABC):
    """
    Classe de base abstraite pour les différents écrans du jeu.
    Force chaque écran à implémenter ces méthodes.
    (Répond à l'exigence ROB d'une classe abstraite)
    """
    def __init__(self, game_context):
        # game_context peut être votre classe Game principale
        # pour permettre aux écrans de communiquer (ex: changer d'écran)
        self.game = game_context

    @abstractmethod
    def handle_input(self, event):
        """Gère les événements Pygame (clavier, souris) pour cet écran."""
        pass

    @abstractmethod
    def update(self):
        """Met à jour la logique de l'écran (ex: animations)."""
        pass

    @abstractmethod
    def draw(self, surface):
        """Dessine l'écran sur la surface Pygame donnée."""
        pass

class GrilleAffiche:
    """
    Affiche la grille du manoir 5x9 et la position du joueur.
    C'est un composant graphique, pas un écran complet.
    """
    def __init__(self, game_logic, image_manager):
        self.game_logic = game_logic  # L'objet contenant l'état du manoir
        self.image_manager = image_manager
        # Définir la taille des tuiles, position de la grille, etc.
        self.tile_size = 64
        self.grid_pos = (50, 50) # Position (x, y) du coin sup-gauche de la grille

    def draw(self, surface):
        """
        Dessine la grille, les pièces découvertes, et le curseur du joueur.
        """
        # 1. Parcourir la grille 5x9 du game_logic (À IMPLÉMENTER)
        # 2. Si une pièce existe :
        #    - Charger son image via self.image_manager.load(piece.image_name, ...)
        #    - La dessiner à la bonne position
        # 3. Si la pièce est noire (pas encore choisie), dessiner un carré noir
        
        # Pour l'instant, on dessine juste un fond de grille vide
        for y in range(9):
            for x in range(5):
                rect = (self.grid_pos[0] + x * self.tile_size,
                        self.grid_pos[1] + y * self.tile_size,
                        self.tile_size, self.tile_size)
                pygame.draw.rect(surface, (40, 40, 40), rect, 1) # Grille grise

        # 4. Dessiner le "curseur" sur la pièce du joueur
        player_pos = self.game_logic.get_player_position() # (col, ligne)
        player_rect = (self.grid_pos[0] + player_pos[0] * self.tile_size, 
                         self.grid_pos[1] + player_pos[1] * self.tile_size, 
                         self.tile_size, 
                         self.tile_size)
        pygame.draw.rect(surface, (255, 255, 0), player_rect, 3) # Curseur jaune

class AfficheInventaire:
    """
    Gère l'affichage des ressources et objets de l'inventaire.
    C'est un composant graphique, pas un écran complet.
    """
    def __init__(self, game_logic, image_manager):
        self.game_logic = game_logic # L'objet contenant l'inventaire du joueur
        self.image_manager = image_manager
        self.font = pygame.font.Font(None, 24) # Police pour les chiffres
        self.inventory_pos = (700, 50) # Position de l'inventaire
        
        # Charger les icônes (on suppose qu'elles existent dans /assets)
        self.icons = {
            "pas": self.image_manager.load("icon_pas.png", (32, 32)),
            # Ajoutez les autres icônes ici...
            # "or": self.image_manager.load("icon_or.png", (32, 32)),
            # "gemme": self.image_manager.load("icon_gemme.png", (32, 32)),
        }

    def draw(self, surface):
        """
        Affiche les objets consommables et permanents.
        """
        # Objets consommables
        pas = self.game_logic.get_steps()
        or_ = self.game_logic.get_gold()
        gemmes = self.game_logic.get_gems()
        cles = self.game_logic.get_keys()
        des = self.game_logic.get_dice()
        
        # Objets permanents
        has_pelle = self.game_logic.has_item("pelle")
        has_marteau = self.game_logic.has_item("marteau")
        has_lockpick = self.game_logic.has_item("lockpick")
        
        # Exemple d'affichage pour les pas :
        y_offset = 0
        if "pas" in self.icons:
            surface.blit(self.icons["pas"], (self.inventory_pos[0], self.inventory_pos[1] + y_offset))
            text_pas = self.font.render(str(pas), True, (255, 255, 255))
            surface.blit(text_pas, (self.inventory_pos[0] + 36, self.inventory_pos[1] + y_offset + 8))
            y_offset += 40 # Espace pour le prochain item

        # ... Répéter pour l'or, les gemmes, les clés, les dés...
        # ... Afficher les icônes des objets permanents si le joueur les possède
        
        # Affichage simple pour les autres (en attendant les icônes)
        text_or = self.font.render(f"Or: {or_}", True, (255, 215, 0))
        surface.blit(text_or, (self.inventory_pos[0], self.inventory_pos[1] + y_offset))
        y_offset += 30
        
        text_gemmes = self.font.render(f"Gemmes: {gemmes}", True, (0, 255, 255))
        surface.blit(text_gemmes, (self.inventory_pos[0], self.inventory_pos[1] + y_offset))
        y_offset += 30


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
        
        # --- Définition des zones ---
        self.GRID_ZONE_WIDTH = 600 # Largeur de la zone noire à gauche
        self.PANEL_START_X = 600   # Point de départ du panneau blanc
        self.PANEL_WIDTH = 400   # Largeur du panneau blanc
        self.PANEL_COLOR = (230, 230, 230) # Couleur du panneau (blanc/gris)
        self.BACKGROUND_COLOR = (20, 20, 20) # Couleur de fond du jeu (noir)
        self.TEXT_COLOR = (0, 0, 0) # Couleur du texte sur le panneau blanc

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
                # Tenter d'ouvrir une porte
                result = self.game_logic.try_open_door()
                
                # Si on doit choisir une pièce (l'ouverture a réussi)
                if result.needs_room_choice:
                    # Demander à la classe Game de changer d'écran
                    self.game.show_room_choice(result.room_options)

    def update(self):
        # Pas de mise à jour logique spécifique à l'UI ici pour l'instant
        pass

    def draw(self, surface):
        # --- Logique de dessin en deux parties ---
        
        # 1. Dessiner le fond noir pour la zone de la grille (gauche)
        grid_background_rect = (0, 0, self.GRID_ZONE_WIDTH, surface.get_height())
        surface.fill(self.BACKGROUND_COLOR, rect=grid_background_rect)

        # 2. Dessiner le panneau blanc pour la zone de l'inventaire (droite)
        inventory_panel_rect = (self.PANEL_START_X, 0, self.PANEL_WIDTH, surface.get_height())
        pygame.draw.rect(surface, self.PANEL_COLOR, inventory_panel_rect)

        # 3. Dessiner la grille de jeu (elle se dessine en (50,50) dans la zone noire)
        self.grille_view.draw(surface) 

        # 4. Afficher le titre "Inventory" sur le panneau blanc
        inv_title = self.title_font.render("Inventory:", True, self.TEXT_COLOR)
        # Positionné par rapport au début du panneau blanc (PANEL_START_X)
        surface.blit(inv_title, (self.PANEL_START_X + 20, 50)) 
        
        # 5. Dessiner l'inventaire sur le panneau blanc
        # Positionné par rapport au début du panneau blanc
        self.inventory_view.draw(surface, (self.PANEL_START_X + 20, 100))

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
        
        # Polices
        self.title_font = pygame.font.Font(None, 36)
        self.room_font = pygame.font.Font(None, 28)
        self.text_font = pygame.font.Font(None, 24)
        
        # Composant Inventaire
        self.inventory_view = AfficheInventaire(game_logic, image_manager)
        
        # Icônes
        self.gem_icon = self.image_manager.load("icon_gemme.png", (20, 20))
        self.dice_icon = self.image_manager.load("icon_des.png", (20, 20))
        
        # --- Définition des zones et couleurs (identiques à GameScreen) ---
        self.PANEL_START_X = 600   # Point de départ du panneau blanc
        self.GRID_ZONE_WIDTH = 600 # Largeur de la zone noire à gauche
        
        self.COLOR_WHITE_PANEL = (230, 230, 230) 
        self.COLOR_BACKGROUND = (0, 0, 0)
        self.COLOR_TEXT = (0, 0, 0)
        self.COLOR_HIGHLIGHT = (0, 150, 255) # Bleu pour la sélection

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
                
                # Tenter de "payer" et de placer la pièce
                if self.game_logic.select_room(chosen_room):
                    # Si réussi, retourner à l'écran de jeu
                    self.game.show_game_screen()
                else:
                    # Optionnel: afficher un message (ex: "Pas assez de gemmes!")
                    print("Pas assez de gemmes !")

    def update(self):
        pass

    def draw(self, surface):
        # --- Toutes les positions en X sont relatives à PANEL_START_X ---
        
        # 1. Dessiner le fond noir pour la zone de gauche
        grid_background_rect = (0, 0, self.GRID_ZONE_WIDTH, surface.get_height())
        surface.fill(self.COLOR_BACKGROUND, rect=grid_background_rect)
        
        # 2. Dessiner le panneau blanc pour la zone de droite
        panel_rect = (self.PANEL_START_X, 0, surface.get_width() - self.GRID_ZONE_WIDTH, surface.get_height())
        pygame.draw.rect(surface, self.COLOR_WHITE_PANEL, panel_rect)

        # 3. Afficher l'inventaire
        inv_title = self.title_font.render("Inventory:", True, self.COLOR_TEXT)
        surface.blit(inv_title, (self.PANEL_START_X + 20, 50)) 
        self.inventory_view.draw(surface, (self.PANEL_START_X + 20, 100)) 

        # 4. Afficher la section "Choose a room to draft"
        draft_title = self.title_font.render("Choose a room to draft", True, self.COLOR_TEXT)
        surface.blit(draft_title, (self.PANEL_START_X + 20, 350)) 

        # 5. Afficher les 3 pièces
        room_size = (150, 150)
        start_x_rooms = self.PANEL_START_X + 20 
        start_y_rooms = 400
        spacing = 180 # Espace horizontal entre les pièces

        for i, room in enumerate(self.room_options):
            x_pos = start_x_rooms + i * spacing 
            
            # Charger l'image de la pièce
            room_img = self.image_manager.load(room.image_name, room_size)
            surface.blit(room_img, (x_pos, start_y_rooms))
            
            # Afficher le nom de la pièce
            room_name_text = self.room_font.render(room.nom, True, self.COLOR_TEXT)
            text_rect = room_name_text.get_rect(center=(x_pos + room_size[0] // 2, start_y_rooms + room_size[1] + 20))
            surface.blit(room_name_text, text_rect)

            # Afficher le coût en gemmes
            cost_text = self.room_font.render(str(room.gem_cost), True, self.COLOR_TEXT)
            cost_x_pos = x_pos + (room_size[0] // 2) # Centré
            surface.blit(self.gem_icon, (cost_x_pos - 15, start_y_rooms + room_size[1] + 40))
            surface.blit(cost_text, (cost_x_pos + 10, start_y_rooms + room_size[1] + 38))

            # Mettre en surbrillance la pièce sélectionnée
            if i == self.selected_index:
                highlight_rect = (x_pos - 5, start_y_rooms - 5, room_size[0] + 10, room_size[1] + 70)
                pygame.draw.rect(surface, self.COLOR_HIGHLIGHT, highlight_rect, 4)
                
                room_name_text_sel = self.room_font.render(room.nom, True, self.COLOR_HIGHLIGHT)
                surface.blit(room_name_text_sel, text_rect)


        # 6. Afficher la section "Redraw"
        redraw_title = self.title_font.render("Redraw", True, self.COLOR_TEXT)
        surface.blit(redraw_title, (self.PANEL_START_X + 20, 650)) 
        
        redraw_text = self.text_font.render("with dice", True, (100, 100, 100)) # Texte en gris
        surface.blit(redraw_text, (self.PANEL_START_X + 20, 690)) 
        surface.blit(self.dice_icon, (self.PANEL_START_X + 20 + redraw_text.get_width() + 5, 688))
