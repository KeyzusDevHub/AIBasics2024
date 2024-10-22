import random
import Obstacle


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

def generate_obstacles(count):
    obstacles = []
    spawned = 0
    while (spawned != count):
        radius = random.randint(OBSTACLE_MIN_RADIUS, OBSTACLE_MAX_RADIUS)

        x = random.randint(radius, SCREEN_WIDTH - radius)
        y = random.randint(radius, SCREEN_HEIGHT - radius)

        if circles_collide(x, y, radius, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, PLAYER_SIZE):
            continue
        
        skip = False
        for obstacle in obstacles:
            if circles_collide(x, y, radius + PLAYER_SIZE * 1.5, obstacle.x, obstacle.y, obstacle.radius):
                skip = True
                break
        
        if skip:
            continue    

        obstacles.append(Obstacle(x, y, radius))
        spawned += 1
    return obstacles

def generate_enemies(count, obstacles):
    enemies = []
    spawned = 0
    while(spawned != count):
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
            enemies.append(Zombie(x, y, radius))
            spawned += 1
    return enemies
