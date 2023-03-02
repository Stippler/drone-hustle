from typing import List
import pygame.math


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

class Drone:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.max_speed = 10.0
        self.max_acceleration = 0.5
        self.radius = 10

    def update(self, target, drones: List["Drone"]):
        # Calculate desired velocity
        target_vec = pygame.Vector2(target[0], target[1])
        desired_velocity = (target_vec - self.pos).normalize() * self.max_speed

        # Avoid collisions with other drones
        for drone in drones:
            if drone is self:
                continue
            to_drone = drone.pos - self.pos
            dist = to_drone.length()
            if dist < self.radius + drone.radius:
                avoid_force = (to_drone / dist) * self.max_acceleration
                desired_velocity -= avoid_force

        # Calculate acceleration and limit to maximum
        self.acceleration = (desired_velocity - self.velocity) / 10.0
        if self.acceleration.length()!=0.0:
            self.acceleration.scale_to_length(min(self.acceleration.length(), self.max_acceleration))

        # Calculate velocity and limit to maximum
        self.velocity += self.acceleration
        self.velocity.scale_to_length(min(self.velocity.length(), self.max_speed))

        # Update position
        self.pos += self.velocity
                
    def draw(self, surface):
        pygame.draw.circle(surface, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), self.radius)

