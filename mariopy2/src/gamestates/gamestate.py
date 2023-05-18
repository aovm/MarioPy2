import pygame
import constants as c

# MAIN SUBSTATE, TRANSITION STATE

class GameState:

    def __init__(self, game) -> None:
        self.getInput = True
        self.game = game
        self.title = ""

        self.end = False
        self.next = None

    def start(self): pass
    def beforeEnd(self): pass

    def update(self, dt, keys): pass
    def render(self, screen: pygame.Surface): pass

    def resetState(self): pass

    # TRANSITION BETWEEN SUB-STATES
    def startTransition(self, dt):
        self.transitioning = True