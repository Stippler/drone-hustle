import pygame
import math
import numpy as np
from drone.drone import Drone

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
BG_COLOR = (255, 255, 255)

# set up clock for FPS control
clock = pygame.time.Clock()

# define Drone class

# set up drone
# drone = Drone(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
drones = [Drone(100, 100), Drone(200, 200), Drone(300, 300)]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    target_pos = pygame.mouse.get_pos()
    screen.fill(BG_COLOR)
    for drone in drones:
        drone.update(target_pos, drones)
        drone.draw(screen)
    pygame.display.flip()
    clock.tick(60)