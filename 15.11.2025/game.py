#game.py
import pygame
from moteur import GameLogic
from interface import GameScreen, RoomChoiceScreen, ImageManager


class Game:
    def __init__(self):
        self.logic = GameLogic()
        self.image_manager = ImageManager()
        
        self.font_small = pygame.font.SysFont("arial", 22)
        self.font_big = pygame.font.SysFont("arial", 32)

        # Fenêtre
        self.screen = pygame.display.set_mode((970, 800)) # <-- CHANGE CECI (de 820 à 970)
        pygame.display.set_caption("Blue Prince")

        # Écran actif
        self.current_screen = GameScreen(self, self.logic, self.image_manager)

    # --- Changer d'écran ---
    def show_room_choice(self, room_options):
        self.current_screen = RoomChoiceScreen(self, self.logic, self.image_manager, room_options)

    def show_game_screen(self):
        self.current_screen = GameScreen(self, self.logic, self.image_manager)

    # --- Boucle du jeu ---
    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                self.current_screen.handle_input(event)

            self.current_screen.update()
            self.current_screen.draw(self.screen)
            pygame.display.flip()
            
            #verifie si le jeu est terminer
                    
            if self.logic.game_over:
                if self.logic.player_won:
                    print("YOU WIN! Reached the Antechamber.")
                else:
                    print("GAME OVER! No more steps.")
                running = False 
           
            
            
            clock.tick(60)

        pygame.quit()
