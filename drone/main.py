import pygame
import math
import numpy as np

# initialize pygame
pygame.init()

# set up window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# set up colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# set up clock for FPS control
clock = pygame.time.Clock()

# define Drone class
class Drone:
    def __init__(self, pos: np.ndarray):
        self.pos = pos
        self.velocity = np.array([0., 0.])
        self.acceleration = np.array([0., 0.])
        self.max_speed = 10
        self.max_acceleration = 0.5
    
    def update(self):
        self.velocity += self.acceleration
        self.pos += self.velocity
    
    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.pos[0]), int(self.pos[1])), 10)


# set up drone
pos = np.array([WINDOW_WIDTH/2, WINDOW_HEIGHT/2])
drone = Drone(pos)

# game loop
while True:
    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # get mouse position
    mouse_pos = pygame.mouse.get_pos()

    # calculate angle to mouse
    dx = mouse_pos[0] - drone.pos[0]
    dy = mouse_pos[1] - drone.pos[1]
    angle = math.atan2(dy, dx)

    # set acceleration towards mouse
    drone.acceleration[0] = math.cos(angle) * 0.1
    drone.acceleration[1] = math.sin(angle) * 0.1

    print(math.cos(angle) * 0.1)
    print(math.sin(angle) * 0.1)
    print(f'{mouse_pos} {drone.pos} {dx} {dy} {drone.acceleration}')

    # update drone
    drone.update()

    # clear screen
    screen.fill(WHITE)

    # draw drone
    drone.draw()

    # update display
    pygame.display.update()

    # limit FPS
    clock.tick(60)
