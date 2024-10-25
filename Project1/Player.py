import pygame
import math
import Bullet

# Ustawienia gracza
PLAYER_COLOR = (0, 255, 0)
PLAYER_SPEED = 2
PLAYER_SIZE = 20
PLAYER_VISION_RADIUS = 1000 
SHOOT_COOLDOWN = 500
PLAYER_SAFE_SPACE = 200
FOG_COLOR = (0, 0, 0, 255)

# Klasa gracza
class Player:
    def __init__(self, pos):
        self.position = pygame.Vector2(pos)
        self.angle = 0
        self.velocity = pygame.Vector2(0, 0)
        self.last_shot_time = 0
        self.health = 1

    def handle_input(self):
        keys = pygame.key.get_pressed()

        self.velocity = pygame.Vector2(0, 0)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity.y = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity.x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity.x = 1

        if self.velocity != pygame.Vector2(0, 0):
            self.velocity.normalize_ip()
        self.velocity *= PLAYER_SPEED

    def move(self):
        self.position += self.velocity

    def check_collision(self, obstacles):
        
        for obstacle in obstacles:
            if Utility.circles_collide(self.position, PLAYER_SIZE, obstacle.position, obstacle.radius):
                
                dist = self.position - obstacle.position
                self.position = obstacle.position + dist.normalize() * (obstacle.radius + PLAYER_SIZE)

    def check_bounds(self, boundaries):
        x = PLAYER_SIZE if self.position.x - PLAYER_SIZE < 0 else self.position.x
        y = PLAYER_SIZE if self.position.y - PLAYER_SIZE < 0 else self.position.y

        x = boundaries[0] - PLAYER_SIZE if x + PLAYER_SIZE > boundaries[0] else x
        y = boundaries[1] - PLAYER_SIZE if y + PLAYER_SIZE > boundaries[1] else y

        self.position = pygame.Vector2(x, y)

    def update_angle(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        rel_mouse_pos = mouse_pos - self.position
        self.angle = math.atan2(-rel_mouse_pos.y, rel_mouse_pos.x)

    def shoot(self, bullets):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= SHOOT_COOLDOWN:

            bullet_vel = pygame.Vector2(math.cos(self.angle), -math.sin(self.angle))
            bullets.append(Bullet.Bullet(self.position, bullet_vel))
            self.last_shot_time = current_time

    def draw(self, screen):
        points = []
        for angle_shift in range(-120, 240, 120):
            angle = self.angle + math.radians(angle_shift)
            angle_vec = pygame.Vector2(math.cos(angle), -math.sin(angle))
            points.append(self.position + PLAYER_SIZE * angle_vec)

        pygame.draw.polygon(screen, PLAYER_COLOR, points)

    def draw_vision(self, fog_surface, obstacles, bounds):
        for obstacle in obstacles:
            d = self.position - obstacle.position
            dist = self.position.distance_to(obstacle.position)

            if dist > obstacle.radius:
                n = pygame.Vector2(d.y, -d.x).normalize()
                
                fog_points = []

                fog_points.append(obstacle.position + obstacle.radius * n)
                fog_points.append(obstacle.position - obstacle.radius * n)
                fog_points.append(self.tangent_to_border(self.position, fog_points[1], bounds))
                fog_points.append(self.tangent_to_border(self.position, fog_points[0], bounds))
                fog_points = self.add_bound_points(fog_points, bounds)

                pygame.draw.circle(fog_surface, FOG_COLOR, obstacle.position, obstacle.radius - 5)
                pygame.draw.polygon(fog_surface, FOG_COLOR, fog_points)

    def add_bound_points(self, f_points, bounds):
        point1 = f_points[2]
        point2 = f_points[3]
        if (point1.x != point2.x and point1.y != point2.y):
            x = list(set([point1.x, point2.x]) & set([0, bounds[0]]))
            y = list(set([point1.y, point2.y]) & set([0, bounds[1]]))
            if len(x) == 0 and self.position.x < point1.x:
                f_points.insert(3, pygame.Vector2(bounds[0], y[0]))
                f_points.insert(3, pygame.Vector2(bounds[0], y[1]))
            elif len(x) == 0 and self.position.x > point1.x:
                f_points.insert(3, pygame.Vector2(0, y[0]))
                f_points.insert(3, pygame.Vector2(0, y[1]))
            elif len(y) == 0 and self.position.y < point1.y:
                f_points.insert(3, pygame.Vector2(x[0], bounds[1]))
                f_points.insert(3, pygame.Vector2(x[1], bounds[1]))
            elif len(y) == 0 and self.position.y > point1.y:
                f_points.insert(3, pygame.Vector2(x[1], 0))
                f_points.insert(3, pygame.Vector2(x[0], 0))
            else:
                f_points.insert(3, pygame.Vector2(x[0], y[0]))
        return f_points

    def is_dead(self):
        return self.health == 0 

    def tangent_to_border(self, start, tangent, bounds):
        direction = tangent - start
        norm_dir = direction.normalize()

        d = pygame.Vector2(0, 0).distance_to(pygame.Vector2(bounds))

        end = start + norm_dir * d

        if end.x < 0:
            end.x = 0
            end.y = start.y + norm_dir.y * (-start.x) / norm_dir.x
        elif end.x > bounds[0]:
            end.x = bounds[0]
            end.y = start.y + norm_dir.y * (bounds[0] - start.x) / norm_dir.x
        
        if end.y < 0:
            end.x = start.x + norm_dir.x * (-start.y) / norm_dir.y
            end.y = 0
        elif end.y > bounds[1]:
            end.x = start.x + norm_dir.x * (bounds[1] - start.y) / norm_dir.y
            end.y = bounds[1]
        
        return end

import Utility
