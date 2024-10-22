# Ustawienia przeciwników
ENEMY_COLOR = (0, 0, 255)
ENEMY_MIN_RADIUS = 10
ENEMY_MAX_RADIUS = 20
ENEMY_COUNT = 5
ENEMY_SPEED = 2
ENEMY_CHANGE_DIR_TIME = [60, 180]
FEARLESS_TIME = 60
FEARLESS_PROBABILITY = 100


# Klasa dla przeciwników
class Zombie:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.vel_x = random.uniform(-1, 1)
        self.vel_y = random.uniform(-1, 1)
        self.change_dir_timer = random.randint(ENEMY_CHANGE_DIR_TIME[0], ENEMY_CHANGE_DIR_TIME[1])
        self.is_fearless = False
        self.fearless_timer = FEARLESS_TIME

    def move(self, obstacles, player):

        self.change_dir_timer -= 1
        if self.change_dir_timer <= 0:
            self.change_dir_timer = random.randint(ENEMY_CHANGE_DIR_TIME[0], ENEMY_CHANGE_DIR_TIME[1])
            self.vel_x = random.uniform(-1, 1)
            self.vel_y = random.uniform(-1, 1)

        if self.is_visible_to_player(player) and not self.is_fearless:
            if (random.randint(1, FEARLESS_PROBABILITY) == 1):
                #self.is_fearless = True
                pass
            closest_obstacle = self.find_closest_obstacle(obstacles)
            if closest_obstacle:
                self.avoid_player_and_obstacle(player, closest_obstacle)
                if circles_collide(self.x, self.y, self.radius, closest_obstacle.x, closest_obstacle.y, closest_obstacle.radius):
                    self.clamp_position(closest_obstacle)
                else:
                    self.clamp_position()
                return
        elif self.is_visible_to_player(player) and self.is_fearless:
            self.fearless_timer -= 1
            if self.fearless_timer < 0:
                self.is_fearless = False
                self.fearless_timer = FEARLESS_TIME

        
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

    def clamp_position(self, obstacle = None):

        if self.x - self.radius < 0:
            self.x = self.radius
            self.change_dir_timer = 0
        if self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.change_dir_timer = 0
        if self.y - self.radius < 0:
            self.y = self.radius
            self.change_dir_timer = 0
        if self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
            self.change_dir_timer = 0
        if obstacle != None:
            dx = self.x - obstacle.x
            dy = self.y - obstacle.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            self.x = obstacle.x + (dx / distance) * (obstacle.radius + self.radius)
            self.y = obstacle.y + (dy / distance) * (obstacle.radius + self.radius)
            self.change_dir_timer = 0

    def avoid_obstacle(self, obstacle):

        self.clamp_position(obstacle)
        self.slide_around_obstacle(obstacle)
        #TODO DODAĆ ODRYWANIE SIĘ OD PRZESZKODY 

    def slide_around_obstacle(self, obstacle):

        vector_to_enemy = pygame.math.Vector2(self.x - obstacle.x, self.y - obstacle.y)
        distance_to_obstacle = vector_to_enemy.length()

        if distance_to_obstacle <= obstacle.radius + self.radius:

            vector_to_enemy.normalize_ip()
            
            tangent_vector = pygame.math.Vector2(-vector_to_enemy.y, vector_to_enemy.x)
            tangent_vector.normalize_ip()

            self.x += tangent_vector.x * ENEMY_SPEED
            self.y += tangent_vector.y * ENEMY_SPEED

    def avoid_player_and_obstacle(self, player, obstacle):
        dx_behind = obstacle.x - player.x
        dy_behind = obstacle.y - player.y
        distance_behind = math.sqrt(dx_behind ** 2 + dy_behind ** 2)

        destination_x = obstacle.x + (dx_behind / distance_behind) * (self.radius + obstacle.radius)
        destination_y = obstacle.y + (dy_behind / distance_behind) * (self.radius + obstacle.radius)

        dx = destination_x - self.x
        dy = destination_y - self.y

        distance = math.sqrt(dx ** 2 + dy ** 2)

        self.vel_x = (dx / distance)
        self.vel_y = (dy / distance)

        self.x += self.vel_x * ENEMY_SPEED
        self.y += self.vel_y * ENEMY_SPEED


    def is_visible_to_player(self, player):

        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)

        visible = (distance <= player.vision_radius)

        if visible:
            for obstacle in obstacles:
                if ray_circle_intersection(self.x, self.y, player.x, player.y, obstacle) != None:
                    visible = False
                    break

        return visible

    def find_closest_obstacle(self, obstacles):

        closest_obstacle = None
        closest_distance = float('inf')
        for obstacle in obstacles:
            distance = math.sqrt((self.x - obstacle.x) ** 2 + (self.y - obstacle.y) ** 2)
            if distance < closest_distance:
                closest_distance = distance
                closest_obstacle = obstacle
        return closest_obstacle

    def draw(self, screen, color = ENEMY_COLOR):
        pygame.draw.circle(screen, color, (self.x, self.y), self.radius)
