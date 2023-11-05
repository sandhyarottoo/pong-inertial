import pygame
import numpy as np
import sys
import os

# global player2_score = 0
# global player1_score = 0
# global max_score = 10





########## CONSTANTS ##########

# Folder path (to 'phys-hackathon-2023/')
# path = '/Users/sandhya/phys-hackathon-2023/'
path = ''
if os.getcwd().split('/')[-1] != "phys-hackathon-2023":
    path = path = '/Users/sandhya/phys-hackathon-2023/' #input("write the path to the 'phys-hackathon-2023' folder here:")


# Constants
WIDTH = 1200
HEIGHT = 800
FPS = 60
MAXSCORE = 10
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
white = (255,255,255)
SURFACE_COLOR = (50, 50, 60)
PLAYER1_COLOR = (255, 50, 50)
PLAYER2_COLOR = (50, 230, 255)
DISK_RADIUS = 300
PLAYER_RADIUS = 305
PLAYER_WIDTH = 8
CIRCLE_COLOR = red
W_PLATFORM = 0.0015 # number is in rad/s, returns deg/s
ACC_PLATFORM = 0
V_INITIAL = -350
PLAYER_VELOCITY = 4
PLAYER_ARC_ANGLE = np.pi / 12  # 90 degrees in radians
MAX_SCORE = 10

player1_angle = -np.pi / 2
player2_angle = -np.pi / 2

#time step for euler integration
dt = 0.0001






########## FUNCTIONS ##########

def cartesian_to_polar(pos_xy):
    if pos_xy.x == 0:
        return 0, 0
    r = np.sqrt(pos_xy.x**2+pos_xy.y**2)
    theta = np.arctan(pos_xy.y/pos_xy.x)
    return pygame.Vector2(r, theta)

def polar_to_cartesian(pos_polar):
    x = pos_polar.x*np.cos(pos_polar.y)
    y = pos_polar.x*np.sin(pos_polar.y)
    return pygame.Vector2(x, y)


#accelerations 
def a_radial(w,r,v_theta):
    return -1*(w**2*r+w*v_theta)

def a_tan(w,v_radial,r,ang_acc):
    return w*v_radial+r*ang_acc

# from: https://stackoverflow.com/questions/42014195/rendering-text-with-multiple-lines-in-pygame
def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.







########## CLASSES ##########
class Player(pygame.sprite.Sprite):
    def __init__(self, color, start_angle, keys):
        super().__init__()
        self.score = 0
        self.color = color
        self.pos = pygame.Vector2(PLAYER_RADIUS, start_angle)
        self.keys = keys
        self.angular_width = PLAYER_ARC_ANGLE
        self.velocity = PLAYER_VELOCITY
        
        self.image = pygame.Surface((2*(PLAYER_RADIUS), 2*(PLAYER_RADIUS)), pygame.SRCALPHA)
        pygame.draw.arc(self.image, self.color,
                        (0, 0, (PLAYER_RADIUS) * 2, (PLAYER_RADIUS) * 2), 
                        self.pos.y - self.angular_width / 2,
                        self.pos.y + self.angular_width / 2,
                        width=PLAYER_WIDTH)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2)
    
    def update(self, keys):
        
        # Move the player on the ring
        if keys[self.keys[0]]:
            self.pos.y -= self.velocity*dt  
        if keys[self.keys[1]]:
            self.pos.y += self.velocity*dt  

        self.image.fill(pygame.SRCALPHA)
        pygame.draw.arc(self.image, self.color,
                        (0, 0, (PLAYER_RADIUS) * 2, (PLAYER_RADIUS) * 2), 
                        self.pos.y - self.angular_width / 2,
                        self.pos.y + self.angular_width / 2,
                        width=PLAYER_WIDTH)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.hasBeenTaken = False
        self.player = None
        self.pos = pygame.Vector2(PLAYER_RADIUS, 2*np.pi*np.random.rand())
    
    def drawShape(self, image, pos, color, angular_width, height):    
        pygame.draw.arc(image, color,
                        (0, 0, (PLAYER_RADIUS) * 2, (PLAYER_RADIUS) * 2), 
                        pos.y - angular_width / 2,
                        pos.y + angular_width / 2,
                        width=height)
        
    def addPlayer(self, player):
        self.player = player
        self.hasBeenTaken = True


class WidePaddle(PowerUp):
    def __init__(self):
        super().__init__()

        #choose your appearance attributes
        self.color = "yellow"
        self.angular_width = np.pi/10
        self.height = 20

        self.image = pygame.Surface((2*(PLAYER_RADIUS) , 2*(PLAYER_RADIUS)), pygame.SRCALPHA)
        self.drawShape(self.image, self.pos, self.color, self.angular_width, self.height)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2)
        
    def update(self, player1, player2):
        #all power up update functions should take both players as input
        if not self.hasBeenTaken:
            self.drawShape(self.image, self.pos, self.color, self.angular_width, self.height)

            if pygame.sprite.collide_mask(self, player1):
                self.addPlayer(player1)
                self.pickup_time = pygame.time.get_ticks()
            elif pygame.sprite.collide_mask(self, player2):
                self.addPlayer(player2)
                self.pickup_time = pygame.time.get_ticks()

            return
        
        #apply effect and measure elapsed time that effect lasts
        self.player.angular_width = 1.6*PLAYER_ARC_ANGLE
        if pygame.time.get_ticks() - self.pickup_time > 5000:
            self.player.angular_width = PLAYER_ARC_ANGLE
            self.kill()

        return

class SpeedPaddle(PowerUp):
    def __init__(self):
        super().__init__()

        #choose your appearance attributes
        self.color = "purple"
        self.angular_width = np.pi/10
        self.height = 20
        self.opposite_player = None

        self.image = pygame.Surface((2*(PLAYER_RADIUS) , 2*(PLAYER_RADIUS)), pygame.SRCALPHA)
        self.drawShape(self.image, self.pos, self.color, self.angular_width, self.height)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2)
        
    def update(self, player1, player2):
        #all power up update functions should take both players as input
        if not self.hasBeenTaken:
            self.drawShape(self.image, self.pos, self.color, self.angular_width, self.height)

            if pygame.sprite.collide_mask(self, player1):
                self.addPlayer(player1)
                self.pickup_time = pygame.time.get_ticks()
                self.opposite_player = player2
            elif pygame.sprite.collide_mask(self, player2):
                self.addPlayer(player2)
                self.pickup_time = pygame.time.get_ticks()
                self.opposite_player = player1

            return
        
        #apply effect and measure elapsed time that effect lasts
        self.opposite_player.velocity = 2*PLAYER_VELOCITY
        if pygame.time.get_ticks() - self.pickup_time > 3000:
            self.opposite_player.velocity = PLAYER_VELOCITY
            self.kill()

        return

power_up_mapping = {
    1: WidePaddle,
    2: SpeedPaddle
}      


class PointCharge(pygame.sprite.Sprite):
    def __init__(self, pos, strength):
        super().__init__()
        self.pos = pos
        self.strength = strength
        self.radius = 15

        self.image = pygame.Surface((2*self.radius, 2*self.radius), pygame.SRCALPHA)
        pygame.draw.circle(self.image, pygame.Color("blue"), (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()

        pos_cartesian = polar_to_cartesian(self.pos)
        self.rect.center = (pos_cartesian.x + WIDTH/2, pos_cartesian.y + HEIGHT/2)

    def computeForce(self, other_pos):

        direction_vec = self.pos - other_pos
        distance = direction_vec.length()
        direction_vec = direction_vec/distance
        
        return (self.strength/distance**2)*direction_vec



class CircleSprite(pygame.sprite.Sprite):
# pos, vel and acc are in polar
    def __init__(self, pos, vel, acc, radius, color):
        super().__init__()
        self.pos = pos
        self.vel = vel
        self.acc = acc
        self.radius = radius
        self.bool_color = False
        self.color = PLAYER1_COLOR

        self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect()

        pos_cartesian = polar_to_cartesian(self.pos)
        self.rect.center = (pos_cartesian.x, pos_cartesian.y)
        
        self.respawn = False
    
    def getForce(self, sources):
        #each object in sources must have a computeForce(self.pos, other.pos) method
        force = pygame.Vector2(0, 0)

        force.y += a_tan(W_PLATFORM, self.vel.x, self.pos.x, ACC_PLATFORM)
        force.x += a_radial(W_PLATFORM, self.pos.x, self.vel.y)
        #could add friction

        for source in sources:
            force += source.computeForce(self.pos)

        return force

        
    def update(self, force_sources,player1,player2):
        
        self.respawn = False

        if pygame.sprite.collide_mask(self,player1) or pygame.sprite.collide_mask(self,player2):
            
            if pygame.sprite.collide_mask(self,player1) and self.color != player1.color:
                self.respawn = True
                player2.score += 1
            if pygame.sprite.collide_mask(self,player2) and self.color != player2.color:
                self.respawn = True
                player1.score += 1
                
            self.bool_color = not self.bool_color


            #collision change of motion
            if self.pos.x < 0:
                self.pos.x = -(PLAYER_RADIUS - PLAYER_WIDTH - self.radius)
            else:
                self.pos.x = (PLAYER_RADIUS - PLAYER_WIDTH - self.radius)
            
            if abs(self.vel.x) < 50 or abs(self.vel.y) > 50:
                self.vel.x *= -1.25
                self.vel.y *= 0.8
            else:
                self.vel.x *= -1.08
        
        # Update the position of the sprite
        self.pos += self.vel*dt
        self.vel += self.acc*dt

        self.acc *= 0
        self.acc += self.getForce(force_sources)

        pos_cartesian = polar_to_cartesian(self.pos)
        
        self.rect.center = (pos_cartesian.x + WIDTH/2, pos_cartesian.y + HEIGHT/2)

        if self.bool_color:
            self.color = PLAYER1_COLOR
        else:
            self.color = PLAYER2_COLOR
            
            
        #when the ball leaves the disk
        if abs(self.pos.x) > PLAYER_RADIUS+PLAYER_WIDTH and player1.score < MAX_SCORE and player2.score < MAX_SCORE:
            if self.color == PLAYER1_COLOR:
                player2.score += 1
            else:
                player1.score += 1
            self.respawn = True

        

        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
      
            
            
class Button():
    def __init__(self, x, y, width, height, function, text, font, inMenu=True ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.function = function
        
        
        self.surface = pygame.Surface((self.width, self.height))
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        if inMenu:
            self.textSurf = font.render(text,True, (40, 40, 40))
            self.colors = {
                'normal': (196,164,132),
                'hover': (156, 124, 92),
                'pressed': (220, 220, 220),
            }
        else:
            self.textSurf = font.render(text,True, (200, 200, 200))
            self.colors = {
                'normal': SURFACE_COLOR,
                'hover' : SURFACE_COLOR,
                'pressed': (130,130,130)
            }
        
    def process(self):
        mouse = pygame.mouse
        mousePos = mouse.get_pos()
        self.surface.fill(self.colors['normal'])
        if self.rect.collidepoint(mousePos):
            self.surface.fill(self.colors['hover'])
            if mouse.get_pressed(num_buttons=3)[0]:
                self.surface.fill(self.colors['pressed'])
                self.function()
                
        self.surface.blit(self.textSurf, [self.rect.width/2 - self.textSurf.get_rect().width/2, 
                                                self.rect.height/2 - self.textSurf.get_rect().height/2])
        screen.blit(self.surface, self.rect)
        



class scoreboard():
    def __init__(self,player1,player2):
        # Scoreboard setup
        self.P1Score = pygame.font.SysFont('verdana', 40).render(f"Player 1: {player1.score}", False, player1.color)
        self.P2Score = pygame.font.SysFont('verdana', 40).render(f"Player 2: {player2.score}", False, player2.color)

    def update_score(self):
        self.P1Score = pygame.font.SysFont('verdana', 40).render(f"Player 1: {player1.score}", False, player1.color)
        self.P2Score = pygame.font.SysFont('verdana', 40).render(f"Player 2: {player2.score}", False, player2.color)







########## GAME ##########

# pygame setup
pygame.init()
pygame.font.init()
pygame.display.set_caption("Pong-Inertial Game")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Setting fonts
font = pygame.font.SysFont('arial', 40)
title = pygame.font.SysFont('verdana', 150).render('Pong-Inertial', False, (250, 220, 210))

# Adding the musics tracks
music = pygame.mixer.music
music.load(path + "MultiMedia/katyusha_8_bit.mp3")
music.play(loops=-1) # -1 loops music indefinitely

#initial conditions in polar coords
pos_polar = pygame.Vector2(DISK_RADIUS*np.random.randint(5,10)/10, np.pi/2)
vel_polar = pygame.Vector2(V_INITIAL, 0)
acc_polar = pygame.Vector2(0,0)

# Create a sprite
circle = CircleSprite(pos_polar, vel_polar, acc_polar, 20, CIRCLE_COLOR)
circles = pygame.sprite.Group()
circles.add(circle)

# Create disk (table top)
disk = pygame.image.load(path+ "MultiMedia/TableTop.png").convert_alpha()
disk = pygame.transform.scale(disk, (DISK_RADIUS*2, DISK_RADIUS*2))

# Create background
bg = pygame.image.load(path+"MultiMedia/background.png").convert_alpha()
bg = pygame.transform.scale_by(bg, (1.1, 1.1))

# create a point charge
# charge = PointCharge(pygame.Vector2(-100, 0), 100000)
charges = pygame.sprite.Group()
# charges.add(charge)

power_ups = pygame.sprite.Group()

# Players
player1_keys = [pygame.K_d, pygame.K_a]
player2_keys = [pygame.K_RIGHT, pygame.K_LEFT]

player1 = Player(PLAYER1_COLOR, 0, player1_keys)
player2 = Player(PLAYER2_COLOR, np.pi, player2_keys)
players = pygame.sprite.Group()
players.add(player1)
players.add(player2)

# Scoreboard setup
P1Score = pygame.font.SysFont('verdana', 40).render(f"Player 1: {player1.score}", False, player1.color)
P2Score = pygame.font.SysFont('verdana', 40).render(f"Player 2: {player1.score}", False, player2.color)

scoreboard = scoreboard(player1,player2)

# Starts function
def start():
    run_game()
    
# returns to menu / intro page
def leave_game():
    music.load(path + "MultiMedia/katyusha_8_bit.mp3")
    music.play(loops=-1) # -1 loops music indefinitely
    run_intro() 

# Opens intro page
def menu():
    run_intro()    
    
# Opens options
def options():
    run_FAQ()
    
# Exits function
def exit():
    pygame.quit()
    sys.exit()

####### UI FUNCTION & GAMEPLAY ########

# To run the menu / intro
def run_intro():
    intro = True
    
    # Making the buttons
    startButton = Button(WIDTH/2 - 100, HEIGHT*(1/3+2/10), 200, 50, start, "Start", font)
    optionButton = Button(WIDTH/2 - 100, HEIGHT*(1/3 + 3/10), 200, 50, options, "FAQ", font)
    exitButton = Button(WIDTH/2 - 100, HEIGHT*(1/3 + 4/10), 200, 50, exit, "Exit", font)
        
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(SURFACE_COLOR)
        screen.blit(title, (WIDTH/2 - title.get_width()/2, HEIGHT*(1/8)))
        startButton.process()
        optionButton.process()
        exitButton.process()
        
        pygame.display.flip()
        clock.tick(FPS)
        
# to run the options page   
def run_FAQ():
    options = True
    
    # making buttons
    menuButton = Button(20, 10, 140, 50, menu, "Menu", font)
    
    # main text
    inst_title = pygame.font.SysFont('verdana', 100).render('FAQ', False, (250, 220, 210))

    inst_text = "Welcome to Pong-Inertial, a fun pong-like game in a non-inertial, rotating reference frame!\n\n"\
                "GAME: colour of the moving disk indicates who must hit it next. If you miss the disk, your opponent gets a point. Points are also given to the opponent if it wasn't your turn to hit it.\n\n"\
                "HOW TO PLAY: Player 1 uses keys a and d to move. Player 2 uses the right and left arrows.\n\n"\
                "POWER-UPS: If the game has gone on for a while, power ups will begin to appear as coloured arcs around the table. To collect it, simply move to it and give it a touch.\n\n"\
                "TYPES OF POWER-UPS: Yellow power-up increases the sides of your arc. Purple power-up increases your opponents speed."    
    inst_font = pygame.font.SysFont('verdana', 20)
    
    while options:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(SURFACE_COLOR)
        screen.blit(inst_title, (WIDTH/2 - inst_title.get_width()/2, HEIGHT*(1/10)))
        blit_text(screen, inst_text, (15, 275), inst_font, (250, 200, 200))
        # screen.blit(instructions, (WIDTH/2-instructions.get_width()/2, HEIGHT/2-instructions.get_height()/2))
        menuButton.process()
        pygame.display.flip()
        clock.tick(FPS)
        
# to run game
def run_game():
    global dt
    # organize music
    music.stop()
    music.load(path + "MultiMedia/Star Wars - Duel Of The Fates 8 - BIT REMIX.mp3")
    music.play(loops=-1) # -1 loops music indefinitely
    
    # reset initial player and circle positions
    player1.pos[1] = 0
    player2.pos[1] = np.pi
    # circle.pos = pygame.Vector2(DISK_RADIUS/10, np.random.sample()*np.pi/2)
    # circle.vel = vel_polar*np.random.sample()
    # circle.acc = acc_polar
    
    # reset background angle
    angle = 0
    
    # reset player score
    player1.score = 0
    player2.score = 0

    powerup_interval = 6000
    last_powerup_time = pygame.time.get_ticks()
    
    # making buttons
    menuButton = Button(20, 10, 140, 50, leave_game, "Menu", font)
    
    text_time = 0
    text = None
    # starting main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                

        # Clears the screen
        screen.fill(SURFACE_COLOR)
        
        # updates background
        bg_rotation = pygame.transform.rotate(bg, angle)
        bg_rect = bg_rotation.get_rect(center = bg_rotation.get_rect(center = (WIDTH//2, HEIGHT//2)).center)
        screen.blit(bg_rotation, bg_rect) # background
        angle -= W_PLATFORM*360/(2*np.pi) * dt *60
        
        # places table top
        screen.blit(disk, (WIDTH/2-300,HEIGHT/2-300))
        
        # updates buttons
        menuButton.process()

        charges.draw(screen)
        
        keys = pygame.key.get_pressed()
        players.update(keys)
        players.draw(screen)
        
        scoreboard.update_score()
        screen.blit(scoreboard.P1Score, (WIDTH/2-scoreboard.P1Score.get_width()-40, 20))
        screen.blit(scoreboard.P2Score, (WIDTH/2+40, 20))
        
        if (len(power_ups) == 0) and (pygame.time.get_ticks() - last_powerup_time > powerup_interval):
            last_powerup_time = pygame.time.get_ticks()
            random_num = np.random.randint(1, len(power_up_mapping)+1)
            current_powerup = power_up_mapping[random_num]()
            power_ups.add(current_powerup)
        
        power_ups.update(player1, player2)
        
        if len(power_ups) != 0 and not power_ups.sprites()[0].hasBeenTaken:
            power_ups.draw(screen)
        
        game_over = False
        current_time = pygame.time.get_ticks()
        if player1.score == MAX_SCORE:
            text = font.render("Congratulations Player 1!",False, black)
            text_time = current_time + 5000
            game_over = True
            circle.respawn = False
        if player2.score == MAX_SCORE:
            text = font.render("Congratulations Player 2!",False, black)
            text_time = current_time + 5000
            game_over = True
            circle.respawn = False
        if circle.respawn:
            text_time = current_time + 2000
            text = pygame.font.SysFont('verdana', 40).render('Respawning in 2 seconds...', True, black)
            circle.respawn = False
            circle.pos = pygame.Vector2(PLAYER_RADIUS/20,np.random.sample()*2*np.pi)
            circle.vel = pygame.Vector2(200 + np.random.sample()*50,np.random.sample()*2)
            circles.update(charges,player1,player2)
        if pygame.time.get_ticks() - text_time < 0:
            circles.draw(screen)
            screen.blit(text, text.get_rect(center = screen.get_rect().center))
            #pygame.display.update()
            
        else:
            circles.update(charges,player1,player2)
            circles.draw(screen)

        if game_over:
            leave_game() # same as menu(), but it changes music
                
            
        # flip() the display to put your work on screen
        pygame.display.flip()
        
        dt = clock.tick(FPS) / 1000
        

run_intro()
pygame.quit()
sys.exit()
