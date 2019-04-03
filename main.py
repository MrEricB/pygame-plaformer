# Jumpy platform game

# Art from Kenny.nl
# Happy Tune by http://oepngameart.org/users/syncopika
# Yippe by http://opengameart.org/users/snabisch


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
        self.dir = path.dirname(path.realpath(__file__))

        #load high score
        with open(path.join(self.dir, HS_FILE),'r+') as f:
            try:
                # there is a high score in the file
                self.highscore = int(f.read())
            except:
                # no high score in the file, set it to 0
                print("can not read file")
                self.highscore = 0

        # load spritesheet 
        img_dir = path.join(self.dir, 'img')
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        # load cloud images
        self.cloud_images = []
        for i in range(1,4):
            self.cloud_images.append(pg.image.load(path.join(img_dir, f'cloud{i}.png')).convert())
        # load sounds and music
        self.snd_dir = path.join(self.dir, 'snd')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Jump3.wav'))
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'boost.wav'))

        

    def new(self):
        # start a new game
        self.score = 0
        # self.all_sprites = pg.sprite.Group()
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.player = Player(self) # self inside () is a reference to the game
        for plat in PLATFORM_LIST:
            Platform(self, *plat)
        self.mob_timer = 0
        # load background music
        pg.mixer.music.load(path.join(self.snd_dir, 'happy_tune.ogg'))
        # spawn so clouds
        for i in range(6):
            c = Cloud(self)
            c.rect.y += 500
        self.run()
    
    def run(self):
        # game loop
        pg.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500) # can use stop() but this it is a hard stop, not a fade

    def update(self):
        # game loop - update
        self.all_sprites.update()
        # spawn a mod ?
        now = pg.time.get_ticks()
        if now - self.mob_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self)
        # hit mobs?
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False, pg.sprite.collide_mask)# collide_mask is a big resouce extpence, if need do box colision then if there is box collison check for mask collision, that whay the game is not always looking for mask collisons
        if mob_hits:
            self.playing = False
        # check if player hits a platform - only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                # make sure player as at least one foot on the platforme, ie no phantom floating because of hit boxes
                if self.player.pos.x < lowest.rect.right + 10 and self.player.pos.x > lowest.rect.left + 10:
                    if self.player.pos.y < lowest.rect.centery: #how high into platform you need to jump to get on top of the platform
                        self.player.pos.y = lowest.rect.top
                        self.player.vel.y = 0
                        self.player.jumping = False

        # if player reaches top 1/4 of screen ie scroll the screen
        if self.player.rect.top <= HEIGHT/4:
            if random.randrange(100) < 10:
                Cloud(self)
            self.player.pos.y += max(abs(self.player.vel.y), 2) # camera movment same as player speed, to keep smooth camera movment
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y /2), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y),2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y),2)
                if plat.rect.top >= HEIGHT:
                    # delete any platforms that are not on the screen
                    plat.kill()
                    self.score += 10

        # if player hits a power up
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for p in pow_hits:
            if p.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False
        
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
            Platform(self, random.randrange(0, WIDTH-width), 
                        random.randrange(-75, -30))

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
            if event.type == pg.KEYUP: # if not holding keydonw jump is not as high, so hold down for hight jump
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def draw(self):
        #game loop draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        # self.screen.blit(self.player.image, self.player.rect) # dont need to blit since we change all_spirts to layger, and added _layer to sprit objs
        self.draw_text(str(self.score), 22, WHITE, WIDTH/2, 15)
        # after drawing everying, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
        pg.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 40, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text("Arrows to move, Space to jump", 22, WHITE, WIDTH/2, HEIGHT/2)
        self.draw_text("Press a key to play", 22, WHITE, WIDTH/2, HEIGHT *3/4)
        self.draw_text(f"High score: {str(self.highscore)}", 22, WHITE, WIDTH/2, 15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def show_go_screen(self):
        # game over/continue screen
        if not self.running: # this is so the X closes the game window when playing instead of going to the game over screen
            return
        pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
        pg.mixer.music.play(loops=-1)
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
        pg.mixer.music.fadeout(500)

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
