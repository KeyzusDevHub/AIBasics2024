import pygame
import random
import math
import Utility

# Ustawienia przeciwników
ENEMY_COLOR_WANDER = (0, 0, 255)
ENEMY_COLOR_HUNT = (128, 0, 0)
ENEMY_COLOR_HIDE = (0, 128, 0)
ENEMY_RADIUS = 15
ENEMY_COUNT = 15
ENEMY_SPEED = 2
ENEMY_RISK_PARAM = 300

# Klasa dla przeciwników
class Zombie:
    def __init__(self, pos):
        self.position = pygame.Vector2(pos)
        self.radius = ENEMY_RADIUS
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.mode = "wander"
        self.steering = SteeringBehaviors(self)
        self.alignment = None

    # Ruch zombie
    def move(self, obstacles, player, boundaries, dt):
        self.velocity = self.new_velocity(obstacles, player, boundaries, dt)

        if self.velocity != pygame.Vector2(0, 0):
            self.velocity.normalize_ip()

        self.position += self.velocity * ENEMY_SPEED

        for obstacle in obstacles:
            if self.position.distance_to(obstacle.position) <= ENEMY_RADIUS + obstacle.radius:
                self.get_outside_obstacle(obstacle)

        self.get_outside_walls(boundaries)
        
        self.mode = self.analyse_current_state(player, obstacles)
        
    # Wyliczanie nowej predkosci 
    def new_velocity(self, obstacles, player, boundaries, dt):
        new_vel = pygame.Vector2(0, 0)
        self.alignment = None
        if self.mode == "wander":
            new_vel += self.steering.Wander()
        elif self.mode == "hide":
            new_vel += 10 * self.steering.Hide(obstacles, player) 
        elif self.mode == "hunt":
            self.alignment = self.steering.Alignment()
            new_vel += self.alignment
            new_vel += 5 * self.steering.Pursuit(player)
        
        new_vel += 0.4 * self.steering.Cohesion()
        new_vel += 0.4 * self.steering.Separation()
        new_vel += 2 * self.steering.ObstacleAvoidance(obstacles)
        new_vel += 3 * self.steering.WallAvoidance(boundaries)

        return new_vel.normalize() * dt + self.velocity

    # Analiza stanu zombie - chodzenie/ucieczka/atak
    def analyse_current_state(self, player, obstacles):

        if self.mode == "hunt":
            return self.mode
        
        if self.is_visible_to_player(player, obstacles) and self.mode == "wander" and self.position.distance_to(player.position) < ENEMY_RISK_PARAM:
            return "hide"
        
        return "wander" if not self.is_visible_to_player(player, obstacles) else self.mode

    # Sprawdzanie czy jest sie w polu zasiegu widzenia gracza
    def is_visible_to_player(self, player, obstacles):

        d = player.position - self.position
        n = pygame.Vector2(d.y, -d.x).normalize()

        hide_mult = 1.5 * ENEMY_RADIUS

        p1 = self.position + hide_mult * n
        p2 = self.position - hide_mult * n

        visible = True
        for obstacle in obstacles:
            if Utility.ray_circle_intersection(p1, player.position, obstacle) != None and Utility.ray_circle_intersection(p2, player.position, obstacle) != None:
                visible = False
                break

        return visible

    # Blokada wejscia w przeszkode
    def get_outside_obstacle(self, obstacle):
        dist = self.position - obstacle.position

        self.position = obstacle.position + dist.normalize() * (obstacle.radius + ENEMY_RADIUS)
    
    # Blokada wejscia w sciane
    def get_outside_walls(self, bounds):
        x = ENEMY_RADIUS if self.position.x - ENEMY_RADIUS < 0 else self.position.x
        y = ENEMY_RADIUS if self.position.y - ENEMY_RADIUS < 0 else self.position.y

        x = bounds[0] - ENEMY_RADIUS if x + ENEMY_RADIUS > bounds[0] else x
        y = bounds[1] - ENEMY_RADIUS if y + ENEMY_RADIUS > bounds[1] else y

        if x != self.position.x and self.velocity.y != 0:
            self.velocity.x = 0
            self.velocity.normalize_ip()
        if y != self.position.y and self.velocity.x != 0:
            self.velocity.y = 0
            self.velocity.normalize_ip()

        self.position = pygame.Vector2(x, y)

    # Ustawienie stanu atakowania gracza
    def set_hunt_state(self):
        self.mode = "hunt"

    # Blokada nakladania sie na siebie przeciwnikow
    def clamp_zombie_positions(self, o_zombie):
        if self == o_zombie:
            return
        
        members_space = self.position - o_zombie.position

        distance = self.position.distance_to(o_zombie.position)

        if distance < ENEMY_RADIUS * 2:
            overlap = ENEMY_RADIUS * 2 - distance

            angle = math.atan2(members_space.y, members_space.x)

            self.position += pygame.Vector2(math.cos(angle) * overlap / 2, math.sin(angle) * overlap / 2)
            o_zombie.position -= pygame.Vector2(math.cos(angle) * overlap / 2, math.sin(angle) * overlap / 2)

    # Rysowanie zalezne od stanu
    def draw(self, screen):
        if self.mode == "hunt":
            pygame.draw.circle(screen, ENEMY_COLOR_HUNT, self.position, self.radius)
        if self.mode == "wander":
            pygame.draw.circle(screen, ENEMY_COLOR_WANDER, self.position, self.radius)
        if self.mode == "hide":
            pygame.draw.circle(screen, ENEMY_COLOR_HIDE, self.position, self.radius)

from SteeringBehaviors import SteeringBehaviors
