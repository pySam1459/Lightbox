import pygame
import pickle
from random import randint
from os.path import exists
from time import sleep
pygame.init()

gamewidth, gameheight = 1000, 1000
screen, clock = pygame.display.set_mode((gamewidth, gameheight)), pygame.time.Clock()
pygame.display.set_caption("Lightbox")
pygame.display.set_icon(pygame.image.load("icon.png"))
tilew, tileh = gamewidth//10, gameheight//10 


def text(surface, text, size, x, y, colour, mfont, centor):
    largeText = pygame.font.SysFont(mfont, int(size))
    if centor:
        textSurf, textRect = text_objects(text, largeText, colour, centor)
        textRect.center = (x, y)
        surface.blit(textSurf, textRect)
    else:
        textSurf = text_objects(text, largeText, colour, centor)
        surface.blit(textSurf, (x, y))


def text_objects(text, font, colour, centor):
    textSurface = font.render(text, True, colour)
    if centor: return textSurface, textSurface.get_rect()
    else: return textSurface


def getmouse():
    return pygame.mouse.get_pos(), pygame.mouse.get_pressed()


def loadSave():
    if not exists("save.pkl"):
        return {"current": [10, 10], "highscore": [-1, -1]}

    with open("save.pkl", "rb") as file:
        return pickle.load(file)

def saveSave(scores):
    with open("save.pkl", "wb") as file:
        pickle.dump(scores, file)


class Tile:
    layouts = {"Light": [[-1, 0], [1, 0], [0, 1], [0, -1]], "Dark": [[-1, -1], [1, -1], [-1, 1], [1, 1]]} # x , y
    statecols = [(255, 255, 255), (35, 35, 35)]

    def __init__(self, i, j, gtype):
        self.i, self.j = i, j
        self.rect = [i*tilew, j*tileh, tilew, tileh]
        
        self.gtype = gtype
        self.state = 0  # 0: white, 1: black

    def active(self, tilearray):
        self.activate(tilearray)
        self.render()
    
    def activate(self, tilearray):
        for di, dj in self.layouts[self.gtype]:
            i, j = self.i + di, self.j + dj 
            if 0 <= i < 10 and 0 <= j < 10:
                tilearray[j][i].state ^= 1
                tilearray[j][i].render()

    def render(self):
        pygame.draw.rect(screen, self.statecols[self.state], self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 1)



class Button:
    def __init__(self, x, y, w, h, col, hover, text=""):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.rect = [x, y, w, h]
        self.text = text

        self.col, self.hovercol = col, hover
        self.hover = False

    def active(self):
        self.render()
        return self.activate()

    def render(self):
        pygame.draw.rect(screen, self.col, self.rect)
        col = self.hovercol if self.hover else (0, 0, 0)
        pygame.draw.rect(screen, col, self.rect, 2)
        text(screen, self.text, self.h//2, self.x + self.w/2, self.y + self.h/2, col, "comicsansms", True)

    def activate(self):
        mousepos, mousepress = getmouse()
        if self.x < mousepos[0] < self.x + self.w and self.y < mousepos[1] < self.y + self.h:
            self.hover = True
            if mousepress[0]:
                return True

        else:
            self.hover = False

        return False


def menu():
    newbut = Button(gamewidth/4, 250, gamewidth/2, gameheight/8, (0, 255, 0), (255, 225, 0), "New Game")
    loadbut = Button(gamewidth/4, 400, gamewidth/2, gameheight/8, (0, 255, 0), (255, 225, 0), "Load Game")
    scores = loadSave()
        
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()

        screen.fill((255, 255, 255))
        text(screen, "Light Box", 100, gamewidth/2, 100, (0, 0, 0), "comicsansms", True)
        
        newtype = newbut.active()
        loadtype = loadbut.active()

        if newtype or loadtype:
            gtype = gameTypes(loadtype, scores)
            if gtype is None: continue 
            
            if newtype:
                scores["current"][gtype == "Dark"] = 10

            return gtype, scores

        pygame.display.update()


def getScoreTexts(tipe, scores):
    if tipe: ## load game
        return "Current Score: {}".format(scores["current"][0]), "Current Score: {}".format(scores["current"][1])

    else:
        h0 = scores["highscore"][0] if scores["highscore"][0] != -1 else "-"
        h1 = scores["highscore"][1] if scores["highscore"][1] != -1 else "-"
        return "Highscore: {}".format(h0), "Highscore: {}".format(h1)


def gameTypes(tipe, scores):
    lightbut = Button(gamewidth/4, 250, gamewidth/4, gameheight/5, (0, 255, 0), (255, 225, 0), "Light")
    darkbut = Button(gamewidth/4, 600, gamewidth/4, gameheight/5, (0, 255, 0), (255, 225, 0), "Dark")
    examples = [[1, 0, 1, 0, 1, 0, 1, 0, 1], [0, 1, 0, 1, 0, 1, 0, 1, 0]]
    check = True

    scoreTexts = getScoreTexts(tipe, scores)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None

        if check:
            if not pygame.mouse.get_pressed()[0]:
                check = False

        else:
            screen.fill((255, 255, 255))
            text(screen, "Game Types", 100, gamewidth/2, 100, (0, 0, 0), "comicsansms", True)

            for j in range(3):
                for i in range(3):
                    col0, col1 = 255 * examples[0][i+j], 255 * examples[1][i+j]
                    pygame.draw.rect(screen, (col0, col0, col0), 
                            (gamewidth/2 + 100 + (gamewidth/15*i), 250 + (gameheight/15*j), gamewidth/15, gameheight/15))
                    pygame.draw.rect(screen, (col1, col1, col1), 
                            (gamewidth / 2 + 100 + (gamewidth / 15 * i), 500 + (gameheight / 15 * j), gamewidth / 15, gameheight / 15))

            pygame.draw.rect(screen, (0, 0, 0), (gamewidth / 2 + 100, 250, gamewidth / 5, gameheight / 5), 2)
            pygame.draw.rect(screen, (0, 0, 0), (gamewidth / 2 + 100, 500, gamewidth / 5, gameheight / 5), 2)

            text(screen, scoreTexts[0], 40, gamewidth/4, 250 + gameheight/5, (0, 0, 0), "comicsansms", False)
            text(screen, scoreTexts[1], 40, gamewidth/4, 600 + gameheight/5, (0, 0, 0), "comicsansms", False)
            
            if lightbut.active():
                return lightbut.text
            
            if darkbut.active():
                return darkbut.text

            pygame.display.update()


def renderScoreScreen(score):
    screen.fill((255, 255, 255))
    text(screen, str(score), 250, gamewidth / 2, gameheight / 2, (0, 0, 0), "comicsansms", True)

    pygame.display.update()
    sleep(1)


def renderGrid(tarray):
    screen.fill((255, 255, 255))
    for row in tarray:
        for tile in row:
            tile.render()

    pygame.display.update()


def checkWin(tarray):
    for row in tarray:
        for tile in row:
            if tile.state:
                return False
    return True


def main():
    while True:
        gtype, scores = menu()
        gindex = gtype == "Dark"

        while scores["current"][gindex] > 0:
            renderScoreScreen(scores["current"][gindex])

            tilearray = [[Tile(i, j, gtype) for i in range(10)] for j in range(10)]
            loops = scores["current"][gindex] 
            for i in range(loops):
                tilearray[randint(0, 9)][randint(0, 9)].activate(tilearray)

            renderGrid(tilearray)

            playing = True
            while playing:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        saveSave(scores)
                        pygame.quit()
                        quit()

                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        tilearray[event.pos[1]//tileh][event.pos[0]//tilew].activate(tilearray)
                        pygame.display.update()
                        loops -= 1
                        
                        cw = checkWin(tilearray)
                        if cw or loops <= 0:
                            if cw:
                                scores["current"][gindex] += 1
                                scores["highscore"][gindex] = max(scores["highscore"][gindex], scores["current"][gindex])

                            elif loops <= 0:
                                scores["current"][gindex] -= 1
                            
                            playing = False

main()
