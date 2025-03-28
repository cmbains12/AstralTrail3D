import pygame
from pygame.event import Event
from pygame.key import ScancodeWrapper
from time import time

from renderer import Renderer
from gamestate import Gamestate
from constants import *

pygame.init()

class AstralApp:
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    FPS = 30
    def __init__(self):
        self.window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.gamestate = Gamestate(self)
        self.rend = Renderer(self, self.window, self.gamestate)
        self.running = False

    def run(self):
        last_time = time()

        self.running = True
        
        while self.running:
            events,keys,mouse = self.get_user_input()

            duration = time() - last_time
            last_time = time()

            self.gamestate.update(events,keys,mouse,duration)

            self.rend.render_frame()
            pygame.display.flip()

            self.clock.tick(self.FPS)

        pygame.quit()

    def get_user_input(self) -> tuple[list[Event],ScancodeWrapper,tuple[int,int]]:
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_rel()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

        return events, keys, mouse


if __name__ == "__main__":
    app = AstralApp()
    app.run()