import os
import pygame
import pygame_menu
from pygame.locals import *
import random, sys
import time

SCR_RECT = Rect(0, 0, 1100, 600)
CELL_SIZE = 10
HEIGHT = SCR_RECT.height // CELL_SIZE
WIDTH = SCR_RECT.width // CELL_SIZE
COL_0 = 14
ROW_0 = 1
DEAD, ALIVE, MARKED, NON_MARKED, NEW_ALIVE, DIED_OUT = 0, 1, 2, 3, 4, 5

#Colors to be used
aqua = (0,255,255)
aquamarine = (69,139,116)
blue = (16,78,139)
brown = (160,82,45)
black = (0,0,0)
deep_pink = (255,20,147)
gold = (255,215,0)
grey = (139,134,130)
lime_green = (127,255,0)
orange = (255,97,3)
pink = (255,181,197)
red = (255,0,0)
teal = (0,128,128)
white = (255,255,255)

# color patterns
# alive, new_alive, dead, marked, died out, grid
p0 = [aqua, orange, brown, grey, white, black]
p1 = [orange, lime_green, teal, red, white, pink]
p2 = [teal, pink, aquamarine, deep_pink, gold, blue]

CURSOR_COLOR = (255,255,255)
SIDE_COLOR = (0,128,128)
WALL_COLOR = (16,78,139)

class LifeGame:
    def __init__(self):

        # global declarations
        global DIED_OUT_COLOR, MARKED_COLOR, NEW_ALIVE_COLOR, DEAD_COLOR, ALIVE_COLOR

        # basic initializations
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption("Conway's Game of Life: Amy's Version")
        self.font = pygame.font.SysFont("FontAwesome", 18)

        # init a universe (2D board) of this life game with dead cells
        self.univ = [[DEAD for x in range(WIDTH)] for y in range(HEIGHT)]

        # init a history board whose cell is marked when a cell is alive once
        self.hist = [[NON_MARKED for x in range(WIDTH)] for y in range(HEIGHT)]

        # initialize data members
        self.generation = 0  
        self.running = False
        self.grid = True
        self.pattern = 0
        self.mode = 0
        self.cursor = [(COL_0+WIDTH)//2, HEIGHT//2]

        # make a clock instance
        clock = pygame.time.Clock()

        # draw walls
        for y in range(HEIGHT):
            pygame.draw.rect(screen, WALL_COLOR, Rect(0,y*CELL_SIZE,CELL_SIZE,CELL_SIZE))
            pygame.draw.rect(screen, WALL_COLOR, Rect((WIDTH-1)*CELL_SIZE,y*CELL_SIZE,CELL_SIZE,CELL_SIZE))
        for x in range(WIDTH):
            pygame.draw.rect(screen, WALL_COLOR, Rect(x*CELL_SIZE,0,CELL_SIZE,CELL_SIZE))
            pygame.draw.rect(screen, WALL_COLOR, Rect(x*CELL_SIZE,(HEIGHT-1)*CELL_SIZE,CELL_SIZE,CELL_SIZE))

        # load color
        self.loadColor(self.pattern)

        # game loop
        while True:
            clock.tick(60)
            self.update()
            self.draw(screen)
            pygame.display.update()

            # change state with mouse motion
            # if shift is pressed, make the cell dead
            # otherwise, make it alive
            mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed[0]:  
                x, y = pygame.mouse.get_pos()
                x, y = x//CELL_SIZE, y//CELL_SIZE
                if x >= COL_0 and y >= ROW_0 and x != WIDTH-1 and y != HEIGHT-1:
                    self.cursor = [x,y]
                    pressed_keys = pygame.key.get_pressed()
                    if pressed_keys[K_RSHIFT] or pressed_keys[K_LSHIFT]:
                        self.univ[y][x] = 0
                    else:
                        self.univ[y][x] = 1

            # event handlers
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    print("Key Pressed")

                    # quit life game
                    if event.key == K_ESCAPE or event.key == K_q:
                        print("Quitting Game: Goodbye!")
                        pygame.quit()
                        sys.exit()

                    # move cursor
                    elif event.key == K_LEFT:
                        self.cursor[0] -= 1
                        if self.cursor[0] <= 0: 
                            self.cursor[0] = 1
                    elif event.key == K_RIGHT:
                        self.cursor[0] += 1
                        if self.cursor[0] >= WIDTH-1: 
                            self.cursor[0] = WIDTH-2
                    elif event.key == K_UP:
                        self.cursor[1] -= 1
                        if self.cursor[1] <= 0:
                            self.cursor[1] = 1
                    elif event.key == K_DOWN:
                        self.cursor[1] += 1
                        if self.cursor[1] >= HEIGHT-1: 
                            self.cursor[1] = HEIGHT-2

                    # toggle state
                    elif event.key == K_SPACE:
                        print("Toggling State of Cell")
                        x,y = self.cursor
                        self.univ[y][x] ^= 1

                    # start/stop simulation
                    elif event.key == K_s:
                        print("Toggling Pause/UnPause.")
                        self.running ^= 1

                    # go to next generation
                    elif event.key == K_n:
                        print("Next Generation")
                        self.running = False
                        self.next()

                    # clear all states
                    elif event.key == K_c:
                        print("Clearing")
                        self.clear()
                        self.running = False

                    # set random states
                    elif event.key == K_r:
                        print("Randomizing")
                        self.rand()

                    # change mode
                    elif event.key == K_m:
                        print("Changing Mode")
                        self.mode+=1

                        if self.mode == 1:
                            MARKED_COLOR = self.c4
                        elif self.mode == 2:
                            NEW_ALIVE_COLOR = self.c2
                        elif self.mode == 3:
                            DIED_OUT_COLOR = self.c5
                        elif self.mode == 4:
                            self.mode = 0
                            DIED_OUT_COLOR = self.c3
                            MARKED_COLOR = self.c3
                            NEW_ALIVE_COLOR = self.c1

                    # on off grid lines
                    elif event.key == K_g:
                        print("Toggling Grid")
                        self.grid^= 1

                    # change color pattern
                    elif event.key == K_p:
                        print("Changing Pattern")
                        self.pattern = (self.pattern+1)%3
                        self.loadColor(self.pattern)

    def loadColor(self, num_pattern):
        global DIED_OUT_COLOR, MARKED_COLOR, NEW_ALIVE_COLOR, DEAD_COLOR, ALIVE_COLOR

        if num_pattern == 0: pattern = p0
        elif num_pattern == 1: pattern = p1
        elif num_pattern == 2:pattern = p2

        self.c1 = pattern[0] 
        self.c2 = pattern[1]
        self.c3 = pattern[2]
        self.c4 = pattern[3]
        self.c5 = pattern[4]
        self.c6 = pattern[5]

        ALIVE_COLOR = self.c1
        DIED_OUT_COLOR = self.c3
        MARKED_COLOR = self.c3
        NEW_ALIVE_COLOR = self.c1
        DEAD_COLOR = self.c3

        if self.mode == 1:
            MARKED_COLOR = self.c4

        elif self.mode == 2:
            MARKED_COLOR = self.c4
            NEW_ALIVE_COLOR = self.c2

        elif self.mode == 3:
            MARKED_COLOR = self.c4
            NEW_ALIVE_COLOR = self.c2
            DIED_OUT_COLOR = self.c5
 
    def clear(self):
        # clear all state and reset generation counter
        self.generation = 0
        for y in range(ROW_0,HEIGHT-1):
            for x in range(COL_0,WIDTH-1):
                self.univ[y][x] = DEAD
                self.hist[y][x] = NON_MARKED

    def rand(self):
        for y in range(ROW_0,HEIGHT-1):
            for x in range(COL_0,WIDTH-1):
                if random.random() < 0.1:
                    self.univ[y][x] = ALIVE

    def update(self):
        if self.running: self.next()

    def next(self):
        # Apply rules to the current universe;
        # Loop through all cells in the universe.
        # In each iteration, count alive cells around and apply rules.
        # If the # of alive cell is 2, keep the state, if it is 3, make it alive,
        # otherwise (i.e., less than 2 or more than 3), make it dead
        next_field = [[False for x in range(WIDTH)] for y in range(HEIGHT)]
        for y in range(ROW_0,HEIGHT-1):
            for x in range(COL_0,WIDTH-1):

                num_alive_cells = self.countAliveCells(x,y)

                if self.univ[y][x] == ALIVE or self.hist[y][x] == DIED_OUT:
                    self.hist[y][x] = MARKED

                if num_alive_cells == 2:
                    next_field[y][x] = self.univ[y][x]

                elif num_alive_cells == 3:
                    if self.univ[y][x] == DEAD:
                        self.hist[y][x] = NEW_ALIVE
                    next_field[y][x] = ALIVE
                else:
                    if self.univ[y][x] == ALIVE:
                        self.hist[y][x] = DIED_OUT 
                    next_field[y][x] = DEAD 

        self.univ = next_field
        self.generation += 1

    def draw(self, screen):
        # show life game cells
        for y in range(ROW_0,HEIGHT-1):
            for x in range(COL_0,WIDTH-1):
                if self.hist[y][x] == NEW_ALIVE:
                    pygame.draw.rect(screen, NEW_ALIVE_COLOR, Rect(x*CELL_SIZE,y*CELL_SIZE,CELL_SIZE,CELL_SIZE))

                elif self.hist[y][x] == DIED_OUT:
                    pygame.draw.rect(screen, DIED_OUT_COLOR, Rect(x*CELL_SIZE,y*CELL_SIZE,CELL_SIZE,CELL_SIZE))

                elif self.univ[y][x] == ALIVE:
                    pygame.draw.rect(screen, ALIVE_COLOR, Rect(x*CELL_SIZE,y*CELL_SIZE,CELL_SIZE,CELL_SIZE))

                elif self.hist[y][x] == MARKED:
                    pygame.draw.rect(screen, MARKED_COLOR, Rect(x*CELL_SIZE,y*CELL_SIZE,CELL_SIZE,CELL_SIZE))
                
                elif self.univ[y][x] == DEAD:
                    pygame.draw.rect(screen, DEAD_COLOR, Rect(x*CELL_SIZE,y*CELL_SIZE,CELL_SIZE,CELL_SIZE))

                if self.grid:
                    pygame.draw.rect(screen, self.c6, Rect(x*CELL_SIZE,y*CELL_SIZE,CELL_SIZE,CELL_SIZE), 1)
        
        # show cursor
        pygame.draw.rect(screen, CURSOR_COLOR, Rect(self.cursor[0]*CELL_SIZE,self.cursor[1]*CELL_SIZE,CELL_SIZE,CELL_SIZE), 1)
        
        # draw menu background
        pygame.draw.rect(screen, SIDE_COLOR,Rect(10,10,460,610))

        # show menu
        screen.blit(self.font.render("CONTROLS:", True, black), (20,10))     
        screen.blit(self.font.render("Space : Alive/Dead", True, black), (20,54))
        screen.blit(self.font.render("S : Start/Stop", True, black), (20,66))
        screen.blit(self.font.render("C : Clear", True, black), (20,78))
        screen.blit(self.font.render("N : Next", True, black), (20,90))
        screen.blit(self.font.render("R : Random", True, black), (20,102))
        screen.blit(self.font.render("P : Pattern", True, black), (20,114))
        if self.mode == 0:
            screen.blit(self.font.render("M : NORMAL", True, black), (20,126))
        elif self.mode == 1:
            screen.blit(self.font.render("M : MARKED", True, black), (20,126))
        elif self.mode == 2:
            screen.blit(self.font.render("M : NEW_ALIVE", True, black), (20,126))
        elif self.mode == 3:
            screen.blit(self.font.render("M : DIED_OUT", True, black), (20,126))
        screen.blit(self.font.render("G : Grid", True, black), (20,139))
        screen.blit(self.font.render("Q : Quit", True, black), (20,149))

        screen.blit(self.font.render("Generation: %d" % self.generation, True, black), (20,185))

        #RULES 
        screen.blit(self.font.render("GAME RULES:", True, black), (20,210))
        screen.blit(self.font.render("If a cell is ON and has fewer than two neighbors that are ON, it turns OFF", True, black), (20,230))
        screen.blit(self.font.render("If a cell is ON and has either two or three neighbors that are ON, it remains ON", True, black), (20, 250))
        screen.blit(self.font.render("If a cell is ON and has more than three neighbors that are ON, it turns OFF", True, black), (20,270))
        screen.blit(self.font.render("If a cell is OFF and has exactly three neighbors that are ON, it turns ON", True, black), (20,290))


    def countAliveCells(self, x, y):
        sum = 0
        sum += self.univ[y-1][x-1]
        sum += self.univ[y-1][x]  
        sum += self.univ[y-1][x+1]
        sum += self.univ[y][x-1]  
        sum += self.univ[y][x+1]  
        sum += self.univ[y+1][x-1]
        sum += self.univ[y+1][x]  
        sum += self.univ[y+1][x+1]
        return sum

if __name__ == "__main__":

    LifeGame()