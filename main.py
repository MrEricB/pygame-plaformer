# Jumpy platform game
import pygame as pg
import random
from settings import *
from sprites import *
from os import path

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init() 
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        # load the high score
        # self.dir = path.dirname(__file__)
        self.dir = path.dirname(path.realpath(__file__))
        print("dir: ", self.dir)
        with open(path.join(self.dir, HS_FILE),'r+') as f:
            try:
                # there is a high score in the file
                self.highscore = int(f.read())
            except:
                # no high score in the file, set it to 0
                print("can not read file")
                self.highscore = 0

    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.player = Player(self) # self inside () is a reference to the game
        self.all_sprites.add(self.player)
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        self.run()
    
    def run(self):
        # game loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # game loop - update
        self.all_sprites.update()
        # check if player hits a platform - only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                self.player.pos.y = hits[0].rect.top
                self.player.vel.y = 0
        # if player reaches top 1/4 of screen
        if self.player.rect.top <= HEIGHT/4:
            self.player.pos.y += abs(self.player.vel.y) # camera movment same as player speed, to keep smooth camera movment
            for plat in self.platforms:
                plat.rect.y += abs(self.player.vel.y)
                if plat.rect.top >= HEIGHT:
                    # delete any platforms that are not on the screen
                    plat.kill()
                    self.score += 10
        # player died
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        # spawn new platforms to keep the same average number of platforms
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            p = Platform(random.randrange(0, WIDTH-width), 
                        random.randrange(-75, -30),
                        width, 20)
            self.platforms.add(p)
            self.all_sprites.add(p)

    def events(self):
        # game loop events
        for event in pg.event.get(): # any events since last time we ask for events
            # check for closing widnow
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()

    def draw(self):
        #game loop draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, WHITE, WIDTH/2, 15)
        # after drawing everying, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 40, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text("Arrows to move, Space to jump", 22, WHITE, WIDTH/2, HEIGHT/2)
        self.draw_text("Press a key to play", 22, WHITE, WIDTH/2, HEIGHT *3/4)
        self.draw_text(f"High score: {str(self.highscore)}", 22, WHITE, WIDTH/2, 15)
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        # game over/continue screen
        if not self.running: # this is so the X closes the game window when playing instead of going to the game over screen
            return
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 40, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text(f"SCORE: {str(self.score)}", 22, WHITE, WIDTH/2, HEIGHT/2)
        self.draw_text("Press a key to play again", 22, WHITE, WIDTH/2, HEIGHT *3/4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("New high score", 22, WHITE, WIDTH/2, HEIGHT/2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.highscore)) 
        else:
            self.draw_text(f"High score: {str(self.highscore)}", 22, WHITE, WIDTH/2, HEIGHT/2 + 40)

        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

# start and run the game    
g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
