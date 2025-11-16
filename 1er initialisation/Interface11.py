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
    (Hérite de AbstractScreen pour l'exigence ROB)
    """
    def __init__(self, game_context, game_logic, image_manager):
        super().__init__(game_context)
        # Crée les composants d'affichage
        self.grille_view = GrilleAffiche(game_logic, image_manager)
        self.inventory_view = AfficheInventaire(game_logic, image_manager)
        self.game_logic = game_logic

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
        surface.fill((20, 20, 20)) # Fond sombre
        self.grille_view.draw(surface)
        self.inventory_view.draw(surface)

class RoomChoiceScreen(AbstractScreen):
    """
    Écran de sélection de pièce (votre 'MenuChoixPlace').
    (Hérite de AbstractScreen pour l'exigence ROB)
    """
    def __init__(self, game_context, game_logic, image_manager, room_options):
        super().__init__(game_context)
        self.game_logic = game_logic
        self.image_manager = image_manager
        self.room_options = room_options # La liste des 3 pièces
        self.selected_index = 0 # Le joueur commence sur la première pièce
        self.font = pygame.font.Font(None, 30)

    def handle_input(self, event):
        """
        Gère la sélection (touches directionnelles) et la validation (Entrée).
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
                    print("Pas assez de gemmes !") #

    def update(self):
        pass

    def draw(self, surface):
        surface.fill((50, 50, 70)) # Fond bleu nuit
        
        # Afficher les 3 pièces
        for i, room in enumerate(self.room_options):
            x_pos = 100 + i * 250
            y_pos = 200
            
            # Charger l'image de la pièce
            room_img = self.image_manager.load(room.image_name, (200, 200))
            surface.blit(room_img, (x_pos, y_pos))
            
            # Afficher le coût en gemmes
            cost_text = self.font.render(f"Coût: {room.gem_cost} G", True, (255, 255, 0))
            surface.blit(cost_text, (x_pos, y_pos + 210))

            # Mettre en surbrillance la pièce sélectionnée
            if i == self.selected_index:
                pygame.draw.rect(surface, (255, 255, 0), (x_pos - 5, y_pos - 5, 210, 240), 4)
