import pygame

# Ustawienia przeszkód
OBSTACLE_COLOR = (255, 0, 0)
OBSTACLE_MIN_RADIUS = 30
OBSTACLE_MAX_RADIUS = 80
OBSTACLE_COUNT = 10

# Klasa do rysowania przeszkód (kolistych)
class Obstacle:
    def __init__(self, pos, radius):
        self.position = pygame.Vector2(pos)
        self.radius = radius
        
    def draw(self, screen):
        pygame.draw.circle(screen, OBSTACLE_COLOR, self.position, self.radius)