import pygame
import random
import sys
import math

# Inicjalizacja pygame
pygame.init()

# Stałe rozmiary ekranu
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
FOG_COLOR = (0, 0, 0, 200)  # Kolor mgły z przezroczystością (200 to poziom alfa)

# Ustawienia przeszkód
OBSTACLE_COLOR = (255, 0, 0)
OBSTACLE_MIN_RADIUS = 30
OBSTACLE_MAX_RADIUS = 80
OBSTACLE_COUNT = 10

# Ustawienia przeciwników
ENEMY_COLOR = (0, 0, 255)
ENEMY_MIN_RADIUS = 10
ENEMY_MAX_RADIUS = 20
ENEMY_COUNT = 5
ENEMY_SPEED = 2
ENEMY_CHANGE_DIR_TIME = [60, 180]

# Ustawienia gracza
PLAYER_COLOR = GREEN
PLAYER_SPEED = 5
PLAYER_SIZE = 20
PLAYER_ROTATION_SPEED = 5
PLAYER_VISION_RADIUS = 300 
SHOOT_COOLDOWN = 500

# Ustawienia pocisków
BULLET_COLOR = BLACK
BULLET_SPEED = 10
BULLET_LIFETIME = 1000

# Utworzenie okna gry
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gra z Mgłą Wojny, Strzelaniem i Inteligentnymi Przeciwnikami")

# Klasa do rysowania przeszkód (kolistych)
class Obstacle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, OBSTACLE_COLOR, (self.x, self.y), self.radius)

#Klasa określająca grupę zombie
class ZombieGroup:
    def __init__(self, leader, members=None):
        self.leader = leader  # Lider grupy (obiekt klasy Enemy)
        self.members = members if members else []  # Pozostali członkowie grupy
        self.hunting_player = False  # Czy grupa poluje na gracza

    def add_member(self, zombie):
        self.members.append(zombie)

    def merge_with(self, other_group):
        if len(self.members) >= len(other_group.members):
            for member in other_group.members:
                self.add_member(member)
            self.add_member(other_group.leader)
            other_group.members.clear() 
            other_group.leader = None
        else:
            for member in self.members:
                other_group.add_member(member)
            other_group.add_member(self.leader)
            self.members.clear()
            self.leader = None

    def check_group_size(self):

        if len(self.members) + 1 >= 5:
            self.hunting_player = True
        else:
            self.hunting_player = False

    def move(self, obstacles, player):

        self.check_group_size()

        if self.hunting_player:
            self.leader.chase_player(player)
        else:
            self.leader.move(obstacles, player)

        for member in self.members:
            member.follow_leader(self.leader)
        
    def draw(self, screen):
        self.leader.draw(screen)

        for member in self.members:
            member.draw(screen)

# Klasa dla przeciwników
class Enemy:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.vel_x = random.uniform(-1, 1)
        self.vel_y = random.uniform(-1, 1)
        self.change_dir_timer = random.randint(ENEMY_CHANGE_DIR_TIME[0], ENEMY_CHANGE_DIR_TIME[1])

    def move(self, obstacles, player):

        self.change_dir_timer -= 1
        if self.change_dir_timer <= 0:
            self.change_dir_timer = random.randint(ENEMY_CHANGE_DIR_TIME[0], ENEMY_CHANGE_DIR_TIME[1])
            self.vel_x = random.uniform(-1, 1)
            self.vel_y = random.uniform(-1, 1)

        if self.is_visible_to_player(player):
            closest_obstacle = self.find_closest_obstacle(obstacles)
            if closest_obstacle:
                self.avoid_obstacle(closest_obstacle)
        
        vel_len = math.sqrt(self.vel_x ** 2 + self.vel_y ** 2) if math.sqrt(self.vel_x ** 2 + self.vel_y ** 2) > 0 else 1
        self.vel_x /= vel_len
        self.vel_y /= vel_len

        self.x += self.vel_x * ENEMY_SPEED
        self.y += self.vel_y * ENEMY_SPEED

        self.clamp_position()

        for obstacle in obstacles:
            if circles_collide(self.x, self.y, self.radius, obstacle.x, obstacle.y, obstacle.radius):
                self.avoid_obstacle(obstacle)

    def chase_player(self, player):

        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            self.vel_x = (dx / distance) 
            self.vel_y = (dy / distance)

        vel_len = math.sqrt(self.vel_x ** 2 + self.vel_y ** 2) if math.sqrt(self.vel_x ** 2 + self.vel_y ** 2) > 0 else 1
        self.vel_x /= vel_len
        self.vel_y /= vel_len

        self.x += self.vel_x * ENEMY_SPEED
        self.y += self.vel_y * ENEMY_SPEED

        self.clamp_position()

        for obstacle in obstacles:
            if circles_collide(self.x, self.y, self.radius, obstacle.x, obstacle.y, obstacle.radius):
                self.avoid_obstacle(obstacle)

    def follow_leader(self, leader):

        dx = leader.x - self.x
        dy = leader.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 50:
            self.vel_x = (dx / distance)
            self.vel_y = (dy / distance)

            vel_len = math.sqrt(self.vel_x ** 2 + self.vel_y ** 2) if math.sqrt(self.vel_x ** 2 + self.vel_y ** 2) > 0 else 1
            self.vel_x /= vel_len
            self.vel_y /= vel_len

            self.x += self.vel_x * ENEMY_SPEED
            self.y += self.vel_y * ENEMY_SPEED

        self.clamp_position()

        for obstacle in obstacles:
            if circles_collide(self.x, self.y, self.radius, obstacle.x, obstacle.y, obstacle.radius):
                self.avoid_obstacle(obstacle)

    def clamp_position(self):

        if self.x - self.radius < 0:
            self.x = self.radius
        if self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
        if self.y - self.radius < 0:
            self.y = self.radius
        if self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius

    # TODO Naprawić unikanie przez zombie terenu
    def avoid_obstacle(self, obstacle):

        dx = self.x - obstacle.x
        dy = self.y - obstacle.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance == 0:
            distance = 0.1

        self.vel_x = (dx / distance)
        self.vel_y = (dy / distance)

        vel_len = math.sqrt(self.vel_x ** 2 + self.vel_y ** 2) if math.sqrt(self.vel_x ** 2 + self.vel_y ** 2) > 0 else 1
        self.vel_x /= vel_len / ENEMY_SPEED
        self.vel_y /= vel_len / ENEMY_SPEED


    def is_visible_to_player(self, player):

        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        
        #TODO Dodać żeby nie wykrywało gracza za przeszkodą

        if distance <= player.vision_radius:
            return True
        
        return False

    def find_closest_obstacle(self, obstacles):

        closest_obstacle = None
        closest_distance = float('inf')
        for obstacle in obstacles:
            distance = math.sqrt((self.x - obstacle.x) ** 2 + (self.y - obstacle.y) ** 2)
            if distance < closest_distance:
                closest_distance = distance
                closest_obstacle = obstacle
        return closest_obstacle

    def draw(self, screen):
        pygame.draw.circle(screen, ENEMY_COLOR, (self.x, self.y), self.radius)

# Klasa gracza
class Player:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.speed = PLAYER_SPEED
        self.angle = 0
        self.target_angle = 0
        self.vel_x = 0
        self.vel_y = 0
        self.vision_radius = PLAYER_VISION_RADIUS
        self.last_shot_time = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()

        self.vel_x = 0
        self.vel_y = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.vel_y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vel_y = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel_x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel_x = 1

        vel_len = math.sqrt(self.vel_x ** 2 + self.vel_y ** 2) if math.sqrt(self.vel_x ** 2 + self.vel_y ** 2) > 0 else 1
        self.vel_x /= vel_len
        self.vel_y /= vel_len

        self.x += self.vel_x * self.speed
        self.y += self.vel_y * self.speed

        if self.x - self.size < 0:
            self.x = self.size
        if self.x + self.size > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.size
        if self.y - self.size < 0:
            self.y = self.size
        if self.y + self.size > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.size

        # TODO Gracz się dziwnie obraca - do naprawy to
        if self.vel_x != 0 or self.vel_y != 0:
            self.target_angle = math.degrees(math.atan2(-self.vel_y, self.vel_x))

    def check_collision(self, obstacles):
        for obstacle in obstacles:
            if circles_collide(self.x, self.y, self.size, obstacle.x, obstacle.y, obstacle.radius):
                self.x -= self.vel_x * self.speed
                self.y -= self.vel_y * self.speed

    # TODO Gracz się dziwnie obraca - albo do naprawy to #maybeboth
    def update_angle(self):
        angle_diff = (self.target_angle - self.angle + 180) % 360 - 180
        if abs(angle_diff) > PLAYER_ROTATION_SPEED:
            self.angle += PLAYER_ROTATION_SPEED * (1 if angle_diff > 0 else -1)
        else:
            self.angle = self.target_angle

    def shoot(self, bullets):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= SHOOT_COOLDOWN:

            bullet_dx = math.cos(math.radians(self.angle))
            bullet_dy = -math.sin(math.radians(self.angle))
            bullets.append(Bullet(self.x, self.y, bullet_dx, bullet_dy))
            self.last_shot_time = current_time

    def draw(self, screen):

        points = [
            (self.x + self.size * math.cos(math.radians(self.angle)),
             self.y - self.size * math.sin(math.radians(self.angle))),
            (self.x + self.size * math.cos(math.radians(self.angle + 120)),
             self.y - self.size * math.sin(math.radians(self.angle + 120))),
            (self.x + self.size * math.cos(math.radians(self.angle - 120)),
             self.y - self.size * math.sin(math.radians(self.angle - 120))),
        ]
        pygame.draw.polygon(screen, PLAYER_COLOR, points)

    def draw_vision(self, fog_surface, obstacles):
        mult = 2
        for angle in range(0, 360 * mult, 1):
            angle = angle / mult
            ray_end_x = self.x + self.vision_radius * math.cos(math.radians(angle))
            ray_end_y = self.y - self.vision_radius * math.sin(math.radians(angle))

            for obstacle in obstacles:
                collision_point = ray_circle_intersection(self.x, self.y, ray_end_x, ray_end_y, obstacle)
                if collision_point:
                    ray_end_x, ray_end_y = collision_point
            
            pygame.draw.line(fog_surface, (0, 0, 0, 0), (self.x, self.y), (ray_end_x, ray_end_y), 2)

# Klasa dla pocisków
class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.vel_x = dx
        self.vel_y = dy

        vel_len = math.sqrt(self.vel_x ** 2 + self.vel_y ** 2)
        self.vel_x /= vel_len
        self.vel_y /= vel_len

        self.lifetime = BULLET_LIFETIME

    def move(self):
        self.x += self.vel_x * BULLET_SPEED
        self.y += self.vel_y * BULLET_SPEED

        self.lifetime -= 16

    def check_collision(self, enemies):

        for enemy in enemies:
            if circles_collide(self.x, self.y, 3, enemy.x, enemy.y, enemy.radius):
                enemies.remove(enemy)
                return True 
    
        for obstacle in obstacles:
            if circles_collide(self.x, self.y, 3, obstacle.x, obstacle.y, obstacle.radius):
                return True
        
        return False

    def draw(self, screen):

        pygame.draw.line(screen, BULLET_COLOR, (self.x, self.y), (self.x + self.vel_x * 5, self.y + self.vel_y * 5), 2)


def circles_collide(x1, y1, r1, x2, y2, r2):
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance < r1 + r2


def ray_circle_intersection(ray_x1, ray_y1, ray_x2, ray_y2, circle):
    dx = ray_x2 - ray_x1
    dy = ray_y2 - ray_y1
    fx = ray_x1 - circle.x
    fy = ray_y1 - circle.y

    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = (fx * fx + fy * fy) - circle.radius * circle.radius

    discriminant = b * b - 4 * a * c
    if discriminant >= 0:
        discriminant = math.sqrt(discriminant)
        t1 = (-b - discriminant) / (2 * a)
        t2 = (-b + discriminant) / (2 * a)

        if t1 >= 0 and t1 <= 1:
            return ray_x1 + t1 * dx, ray_y1 + t1 * dy
        if t2 >= 0 and t2 <= 1:
            return ray_x1 + t2 * dx, ray_y1 + t2 * dy

    return None

#TODO Do poprawy na razie spawnują się totalnie losowo - dodać im dobry spacing oraz brak możliwości spawnowania w miejscu spawnu gracza
def generate_obstacles(count):
    obstacles = []
    for _ in range(count):
        radius = random.randint(OBSTACLE_MIN_RADIUS, OBSTACLE_MAX_RADIUS)
        x = random.randint(radius, SCREEN_WIDTH - radius)
        y = random.randint(radius, SCREEN_HEIGHT - radius)
        obstacles.append(Obstacle(x, y, radius))
    return obstacles

def generate_enemies(count, obstacles):
    enemies = []
    for _ in range(count):
        radius = random.randint(ENEMY_MIN_RADIUS, ENEMY_MAX_RADIUS)
        x = random.randint(radius, SCREEN_WIDTH - radius)
        y = random.randint(radius, SCREEN_HEIGHT - radius)

        # Sprawdzanie, czy nowe koło (przeciwnik) nie koliduje z przeszkodami
        collision = False
        for obstacle in obstacles:
            if circles_collide(x, y, radius, obstacle.x, obstacle.y, obstacle.radius):
                collision = True
                break

        if not collision:
            enemies.append(Enemy(x, y, radius))
    return enemies


obstacles = generate_obstacles(OBSTACLE_COUNT)
enemies = generate_enemies(ENEMY_COUNT, obstacles)

player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, PLAYER_SIZE)


def game_loop():
    clock = pygame.time.Clock()
    running = True

    fog_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    bullets = []
    zombie_groups = []

    enemies = [Enemy(random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50), 20) for _ in range(10)]


    while running:
        screen.fill(WHITE)

        for obstacle in obstacles:
            obstacle.draw(screen)

        for bullet in bullets:
            bullet.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.handle_input()

        player.check_collision(obstacles)

        player.update_angle()

        if pygame.key.get_pressed()[pygame.K_SPACE]:
            player.shoot(bullets)

        for bullet in bullets[:]:
            bullet.move()

            if bullet.check_collision(enemies):
                bullets.remove(bullet)
            elif bullet.lifetime <= 0:
                bullets.remove(bullet)



        for zombie in enemies:
            if not any(zombie in group.members or zombie == group.leader for group in zombie_groups):
                nearby_zombies = [z for z in enemies if z != zombie and math.sqrt((z.x - zombie.x) ** 2 + (z.y - zombie.y) ** 2) < 100]
                if nearby_zombies:
                    leader = zombie
                    group = ZombieGroup(leader)
                    for z in nearby_zombies:
                        group.add_member(z)
                    zombie_groups.append(group)


        for i, group in enumerate(zombie_groups):
            for j, o_group in enumerate(zombie_groups):
                if i != j and group.leader != None and o_group.leader != None:
                    distance = math.sqrt((group.leader.x - o_group.leader.x) ** 2 + (group.leader.y - o_group.leader.y) ** 2)
                    if distance < 100:
                        group.merge_with(o_group)

        for group in zombie_groups:
            if group.leader == None:
                zombie_groups.remove(group)

        for group in zombie_groups:
            group.move(obstacles, player)
            group.draw(screen)

        for zombie in enemies:
            if not any(zombie in group.members or zombie == group.leader for group in zombie_groups):
                zombie.move(obstacles, player)
                zombie.draw(screen)

        fog_surface.fill((0, 0, 0, 150))

        player.draw_vision(fog_surface, obstacles)

        screen.blit(fog_surface, (0, 0))

        player.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
