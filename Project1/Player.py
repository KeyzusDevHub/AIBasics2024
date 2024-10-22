import pygame

# Ustawienia gracza
PLAYER_COLOR = (0, 255, 0)
PLAYER_SPEED = 5
PLAYER_SIZE = 20
PLAYER_ROTATION_SPEED = 5
PLAYER_VISION_RADIUS = 1000 
SHOOT_COOLDOWN = 500

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

    def check_collision(self, obstacles):
        for obstacle in obstacles:
            if circles_collide(self.x, self.y, self.size, obstacle.x, obstacle.y, obstacle.radius):
                self.x -= self.vel_x * self.speed
                self.y -= self.vel_y * self.speed

    def update_angle(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.x, mouse_y - self.y
        self.angle = math.degrees(math.atan2(-rel_y, rel_x))

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
        mult = 10
        for angle in range(0, 360 * mult, 1):
            angle = angle / mult
            ray_end_x = self.x + self.vision_radius * math.cos(math.radians(angle))
            ray_end_y = self.y - self.vision_radius * math.sin(math.radians(angle))

            for obstacle in obstacles:
                collision_point = ray_circle_intersection(self.x, self.y, ray_end_x, ray_end_y, obstacle)
                if collision_point:
                    ray_end_x, ray_end_y = collision_point
            
            pygame.draw.line(fog_surface, (0, 0, 0, 0), (self.x, self.y), (ray_end_x, ray_end_y), 2)