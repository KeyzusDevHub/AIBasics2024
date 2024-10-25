import pygame
import random
import math

# Ustawienia przeciwników
ENEMY_COLOR = (0, 0, 255)
LEADER_COLOR = (255, 255, 0)
ENEMY_RADIUS = 15
ENEMY_COUNT = 40
ENEMY_SPEED = 2
WANDER_RANGE = [300, 500]
ENEMY_RISK_PARAM = 10 


# Klasa dla przeciwników
class Zombie:
    def __init__(self, pos):
        self.position = pygame.Vector2(pos)
        self.radius = ENEMY_RADIUS
        self.velocity = pygame.Vector2(0, 0)
        self.mode = "wander"
        self.point = None
        self.ignore_player = False
        self.leader = None

    def move(self, obstacles, player, boundaries):
        self.generate_new_destination(obstacles, player, boundaries)
        self.move_towards_point(obstacles)
        self.analyse_current_state(player, obstacles)

    def analyse_current_state(self, player, obstacles):

        if self.mode == "hunt":
            return
        
        if self.leader != None and self.leader != self:
            self.mode = "follow"
        
        if (Utility.circles_collide(self.point, 2, self.position, 2) or (not self.is_visible_to_player(player, obstacles) and self.mode == "hide")):
            self.point = None
            if random.randint(1, 100) > ENEMY_RISK_PARAM:
                self.mode = "risk-wander"
            else:
                self.mode = "wander"
        
        if self.is_visible_to_player(player, obstacles) and self.mode == "wander":
            self.mode = "hide"
            self.point = None

    def move_towards_point(self, obstacles):
        if (self.point - self.position) != pygame.Vector2(0, 0):
            self.velocity = (self.point - self.position).normalize()
        else:
            self.velocity = pygame.Vector2(0, 0)

        for obstacle in obstacles:
            if (self.position + self.velocity * ENEMY_SPEED).distance_to(obstacle.position) <= ENEMY_RADIUS + obstacle.radius:
                self.get_outside_obstacle(obstacle)
                self.slide_around_obstacle(obstacle)
                break

        self.position += self.velocity * ENEMY_SPEED

    def is_visible_to_player(self, player, obstacles):
        visible = True
        for obstacle in obstacles:
            if Utility.ray_circle_intersection(self.position, player.position, obstacle) != None:
                visible = False
                break

        return visible

    def get_outside_obstacle(self, obstacle):
        dist = self.position - obstacle.position

        self.position = obstacle.position + dist.normalize() * (obstacle.radius + ENEMY_RADIUS)

    def slide_around_obstacle(self, obstacle):

        tangent_vector = self.tangent_vector_angle(obstacle)

        self.velocity = tangent_vector

    def tangent_vector_angle(self, obstacle):
        vector_to_enemy = self.position - obstacle.position

        vector_to_enemy.normalize_ip()

        t_vec = pygame.Vector2(-vector_to_enemy.y, vector_to_enemy.x)
        direct = (self.point - self.position).normalize()
        if t_vec * direct < 0:
            t_vec *= -1

        return t_vec

    def generate_new_destination(self, obstacles, player, boundaries):
        if (self.mode == "wander" or self.mode == "risk-wander") and self.point == None:
            self.point = self.generate_wander_point(obstacles, boundaries)
        elif self.mode == "follow":
            self.point = self.leader.position
        elif self.mode == "hide" and self.point == None:
            self.point = self.generate_hiding_point(obstacles, player)
        elif self.mode == "hunt":
            self.point = player.position
        
    #TODO Można poprawić algorytm wyznaczania przeszkody - na razie najbliższa
    def generate_hiding_point(self, obstacles, player):
        closest = float('inf')
        closest_obstacle = None
        for obstacle in obstacles:
            dist_to_obstacle = self.position.distance_to(obstacle.position)
            if dist_to_obstacle < closest:
                closest_obstacle = obstacle
                closest = dist_to_obstacle
        
        hiding_point = closest_obstacle.position + (closest_obstacle.position - player.position).normalize() * (ENEMY_RADIUS + closest_obstacle.radius)

        return hiding_point

    def generate_wander_point(self, obstacles, boundaries):
        
        generated_point = self.position + pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * random.randint(WANDER_RANGE[0], WANDER_RANGE[1])
        
        while (not self.check_if_valid(generated_point, obstacles, boundaries)):
            generated_point = self.position + pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * random.randint(WANDER_RANGE[0], WANDER_RANGE[1])
        
        return generated_point

    def check_if_valid(self, point, obstacles, bounds):
        if (point.x - ENEMY_RADIUS < 0 or point.y - ENEMY_RADIUS < 0):
            return False
        elif (point.x + ENEMY_RADIUS > bounds[0] or point.y + ENEMY_RADIUS > bounds[1]):
            return False
        
        for obstacle in obstacles:
            if Utility.circles_collide(point, self.radius, obstacle.position, obstacle.radius):
                return False
        return True
    
    def set_leader(self, l):
        self.leader = l

    def set_hunt_state(self):
        self.mode = "hunt"

    def clamp_zombie_positions(self, o_zombie):
        if self.leader == None or o_zombie.leader == None:
            return
        if self.leader == self or o_zombie.leader == o_zombie:
            return
        if self == o_zombie:
            return
        
        members_space = self.position - o_zombie.position

        distance = self.position.distance_to(o_zombie.position)

        if distance < ENEMY_RADIUS * 2:
            overlap = ENEMY_RADIUS * 2 - distance

            angle = math.atan2(members_space.y, members_space.x)

            self.position += pygame.Vector2(math.cos(angle) * overlap / 2, math.sin(angle) * overlap / 2)
            o_zombie.position -= pygame.Vector2(math.cos(angle) * overlap / 2, math.sin(angle) * overlap / 2)

    def draw(self, screen):
        if self.leader == self:
            pygame.draw.circle(screen, LEADER_COLOR, self.position, self.radius)
        else:
            pygame.draw.circle(screen, ENEMY_COLOR, self.position, self.radius)

import Utility