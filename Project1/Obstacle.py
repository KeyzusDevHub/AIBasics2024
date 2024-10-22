# Ustawienia przeszkód
OBSTACLE_COLOR = (255, 0, 0)
OBSTACLE_MIN_RADIUS = 30
OBSTACLE_MAX_RADIUS = 80
OBSTACLE_COUNT = 10

# Klasa do rysowania przeszkód (kolistych)
class Obstacle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, OBSTACLE_COLOR, (self.x, self.y), self.radius)