import pygame
import random
import sys
import math
import Utility
import Player
import Zombie
import Obstacle

# Stałe rozmiary ekranu
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FOG_COLOR = (0, 0, 0, 150)

# Inicjalizacja pygame
pygame.init()

# Utworzenie okna gry
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gra o strzelaniu przez trójkątnego gracza do okrągłych zombie z kolistymi przeszkodami, mgłą wojny i sztuczną inteligencją opartą o emergentne zachowania")

obstacles = Utility.generate_obstacles(Obstacle.OBSTACLE_COUNT)
enemies = Utility.generate_enemies(Zombie.ENEMY_COUNT, obstacles)

player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, Player.PLAYER_SIZE)


def game_loop():
    clock = pygame.time.Clock()
    running = True

    fog_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    bullets = []
    zombie_groups = []

    enemies = [Zombie(random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50), 20) for _ in range(10)]


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

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            player.shoot(bullets)

        for bullet in bullets[:]:
            bullet.move()

            if bullet.check_collision(enemies, zombie_groups):
                bullets.remove(bullet)
            elif bullet.lifetime <= 0:
                bullets.remove(bullet)



        for zombie in enemies:
            if not any(zombie in group.members or zombie == group.leader for group in zombie_groups):
                nearby_zombies = [z for z in enemies if z != zombie and math.sqrt((z.x - zombie.x) ** 2 + (z.y - zombie.y) ** 2) < 100]
                if nearby_zombies:
                    leader = zombie
                    group = ZombieGroup(leader)
                    enemies.remove(leader)
                    for z in nearby_zombies:
                        group.add_member(z)
                        enemies.remove(z)
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

        fog_surface.fill(FOG_COLOR)

        player.draw_vision(fog_surface, obstacles)

        screen.blit(fog_surface, (0, 0))

        player.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
