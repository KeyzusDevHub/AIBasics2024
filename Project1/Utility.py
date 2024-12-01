import Obstacle
import Player
from random import randint
import math
import pygame
import Zombie

# Kolizje miedzy kolami
def circles_collide(pos1, r1, pos2, r2):
    distance = pos1.distance_to(pos2)

    return distance < r1 + r2

# Kolizja miedzy promieniem a kolem
def ray_circle_intersection(ray1, ray2, circle):
    d_ray = ray2 - ray1
    d_ray_cir = ray1 - circle.position

    a = d_ray.dot(d_ray)
    b = 2 * d_ray.dot(d_ray_cir)
    c = d_ray_cir.dot(d_ray_cir) - circle.radius ** 2

    discriminant = b ** 2 - 4 * a * c
    if discriminant >= 0:
        discriminant = math.sqrt(discriminant)
        t1 = (-b - discriminant) / (2 * a)
        t2 = (-b + discriminant) / (2 * a)

        if t1 >= 0 and t1 <= 1:
            return ray1 + pygame.Vector2(t1 * d_ray.x, t1 * d_ray.y)
        if t2 >= 0 and t2 <= 1:
            return ray1 + pygame.Vector2(t2 * d_ray.x, t2 * d_ray.y)

    return None

# Generowanie przeszkod
def generate_obstacles(boundaries):
    obstacles = []
    spawned = 0

    while (spawned != Obstacle.OBSTACLE_COUNT):
        radius = randint(Obstacle.OBSTACLE_MIN_RADIUS, Obstacle.OBSTACLE_MAX_RADIUS)
        r_e_o = radius + Zombie.ENEMY_RADIUS * 2
        
        position = pygame.Vector2(randint(r_e_o, boundaries[0] - r_e_o), randint(r_e_o, boundaries[1] - r_e_o))
        
        player_starting_pos = pygame.Vector2(boundaries[0] // 2, boundaries[1] // 2)

        if circles_collide(position, radius, player_starting_pos, Player.PLAYER_SIZE):
            continue
        
        skip = False
        for obstacle in obstacles:
            if circles_collide(position, radius + Player.PLAYER_SIZE * 2, obstacle.position, obstacle.radius):
                skip = True
                break
        
        if skip:
            continue    

        obstacles.append(Obstacle.Obstacle(position, radius))
        spawned += 1

    return obstacles

# Generowanie przeciwnikow
def generate_enemies(obstacles, boundaries):
    enemies = []
    spawned = 0
    while(spawned != Zombie.ENEMY_COUNT):
        radius = Zombie.ENEMY_RADIUS
        position = pygame.Vector2(randint(radius, boundaries[0] - radius), randint(radius, boundaries[1] - radius))

        collision = False

        player_spawn = pygame.Vector2(boundaries[0] // 2, boundaries[1] // 2)
        if circles_collide(position, radius, player_spawn, Player.PLAYER_SAFE_SPACE):
            continue

        for obstacle in obstacles:
            if circles_collide(position, radius, obstacle.position, obstacle.radius):
                collision = True
                break

        if not collision:
            enemies.append(Zombie.Zombie(position))
            spawned += 1
    return enemies
