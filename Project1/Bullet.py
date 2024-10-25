import pygame
# Ustawienia pocisków
BULLET_COLOR = (0, 0, 0)
BULLET_SPEED = 10
BULLET_SIZE = 5


# Klasa dla pocisków
class Bullet:
    def __init__(self, pos, vel):
        self.position = pygame.Vector2(pos)
        self.velocity = vel.normalize()

    def move(self):
        self.position += self.velocity * BULLET_SPEED

    def check_collision(self, enemies, obstacles, boundaries, player):
                
        for enemy in enemies:
            if Utility.circles_collide(self.position, BULLET_SIZE, enemy.position, enemy.radius):
                if enemy.leader == enemy:
                    followers = list(filter(lambda x: x.leader == enemy and x.leader != x, enemies))
                    if followers:
                        followers_sorted = sorted(followers, key=lambda x: x.position.distance_to(player.position))
                        new_leader = followers_sorted[0]
                        for member in followers:
                            member.set_leader(new_leader)
                        if enemy.mode == "hunt":
                            new_leader.set_hunt_state()
                enemies.remove(enemy)
                return True 

        for obstacle in obstacles:
            if Utility.circles_collide(self.position, BULLET_SIZE, obstacle.position, obstacle.radius):
                return True
        

        return self.check_out_of_bounds(boundaries)

    def check_out_of_bounds(self, boundaries):
        out_of_x = self.position.x < 0 or self.position.x > boundaries[0]
        out_of_y = self.position.y < 0 or self.position.y > boundaries[1]
        return out_of_x or out_of_y

    def draw(self, screen):

        pygame.draw.line(screen, BULLET_COLOR, self.position, self.position + self.velocity * BULLET_SIZE, 2)

import Utility