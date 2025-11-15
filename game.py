import pygame
from moteur import GameLogic
from interface import GameScreen, RoomChoiceScreen, ImageManager


class Game:
    def __init__(self):
        self.logic = GameLogic()
        self.image_manager = ImageManager()

        # Fenêtre
        self.screen = pygame.display.set_mode((1000, 800))
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
            clock.tick(60)

        pygame.quit()
