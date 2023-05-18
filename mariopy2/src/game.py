import pygame, time, os
import constants as c
import resources as r
import gamestates.level1 as l1
import gamestates.menu as menu
import gamestates.loading as load
import viewport as vw

class Game:

    def __init__(self) -> None:
        pygame.init()

        self.window_w, self.window_h = (c.WINDOW_WIDTH, c.WINDOW_HEIGHT)
        self.screen = pygame.display.set_mode( (self.window_w, self.window_h) )
        pygame.display.set_caption(c.WINDOW_TITLE)

        self.res: dict = r.load()
        # self.viewport = Viewport(self.screen, self.res)

        self.mainMenu = menu.Menu(self)
        self.loading = load.Loading(self)
        self.gameOver = None
        self.levels = [l1.Level1(self)]
        self.level_index = -1

        self.currentState = None

        self.maxScore = 0

        self.marioLives = 3
        self.totalScore = 0
        self.totalCoins = 0

        self.fontPath = self.res['UI']['font_path']

        self.running, self.playing = False, False
        self.keys = pygame.key.get_pressed()

        self.dt = 0.0
        self.prev_dt = 0.0
        self.prev_time = time.time()
        self.accumulator = 0.0

    def start(self):
        if self.running: return
        self.running, self.playing = True, True
        
        if self.currentState == None:
            self.currentState = self.mainMenu
        self.game_loop()

    def game_loop(self):
        while self.playing:
            self.updateTime()
            self.get_events()
            self.update()
            self.render()

    def get_events(self) -> None:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.playing = False
                self.running = False
        self.keys = pygame.key.get_pressed()

    DT = 1 / c.TARGET_FPS

    def update(self) -> None:
        self.accumulator += self.dt
        while self.accumulator >= self.DT:
            self.currentState.update(self.DT, self.keys if self.currentState.getInput else None)
            self.accumulator -= self.DT

    def render(self) -> None:
        self.currentState.render(self.screen)
        pygame.display.flip()

    def updateTime(self) -> None:
        ctime = time.time() # seconds
        self.prev_dt = self.dt
        self.dt = ctime - self.prev_time
        self.prev_time = ctime

    def nextLevel(self):
        self.level_index += 1
        cLevel = self.levels[self.level_index]
        self.loading.assignData(cLevel)
        self.loading.start()
        self.currentState = self.loading

    def grabCoin(self):
        self.totalCoins += 1

    def addScore(self, amount: int):
        self.totalScore += amount

    def addMarioLive(self):
        self.marioLives += 1
        if self.marioLives > 127:
            self.marioLives = 127

    # WIP
    def reloadLevel(self):
        cLevel = self.currentLevel
        self.loading.assignData(cLevel)

    # WIP
    def restartGame(self):
        self.currentState = self.mainMenu
        self.marioLives = 3
        self.totalScore = 0
        self.totalCoins = 0
        self.level_index = -1

    def drawUIText(self, text, pos, color=c.WHITE, scaling=1):
        fnt = pygame.font.Font(self.fontPath, int(c.sizeUI() * scaling))

        x, y = pos
        absPos = c.adjustWindow(x, y)

        render = fnt.render(text, False, color)
        render = render.convert_alpha()
        
        self.screen.blit(render, absPos)

    def drawUIIcon(self, icon, pos):
        x, y = pos
        absPos = c.adjustWindow(x, y)

        w = c.WINDOW_WIDTH * icon.get_width() / c.VIEWPORT_WIDTH
        h = c.WINDOW_WIDTH * icon.get_height() / c.VIEWPORT_HEIGHT

        iconS = pygame.transform.scale(icon, (w, h))

        self.screen.blit(iconS, absPos)

if __name__ == '__main__':
    g = Game()
    while g.running:
        g.game_loop()