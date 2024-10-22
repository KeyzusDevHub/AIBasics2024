# Ustawienia pocisków
BULLET_COLOR = BLACK
BULLET_SPEED = 10
BULLET_LIFETIME = 1000


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

    def check_collision(self, enemies, zombie_groups):

        for enemy in enemies:
            if circles_collide(self.x, self.y, 3, enemy.x, enemy.y, enemy.radius):
                enemies.remove(enemy)
                return True 

        for group in zombie_groups:
            if circles_collide(self.x, self.y, 3, group.leader.x, group.leader.y, group.leader.radius):
                group.new_leader()
                return True
            
            for member in group.members:
                if circles_collide(self.x, self.y, 3, member.x, member.y, member.radius):
                    group.members.remove(member)
                    return True

        for obstacle in obstacles:
            if circles_collide(self.x, self.y, 3, obstacle.x, obstacle.y, obstacle.radius):
                return True
        
        return False

    def draw(self, screen):

        pygame.draw.line(screen, BULLET_COLOR, (self.x, self.y), (self.x + self.vel_x * 5, self.y + self.vel_y * 5), 2)