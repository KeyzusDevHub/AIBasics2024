import pygame
import random
import sys
import math
import Utility
import Player
import Zombie
import Obstacle

# Stałe rozmiary ekranu
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800

# Kolory
BACKGROUND_COLOR = (255, 255, 255)
FOG_COLOR = (0, 0, 0, 0)

# Brzegi ekranu
BOUNDARIES = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Inicjalizacja pygame
pygame.init()

# Utworzenie okna gry
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gra o strzelaniu przez trójkątnego gracza do okrągłych zombie z kolistymi przeszkodami, mgłą wojny i sztuczną inteligencją opartą o emergentne zachowania")

def lose_screen(screen):
    font = pygame.font.Font(None, 150)

    text_surface = font.render("Zombie win", True, (255, 0, 0))

    text_rect = text_surface.get_rect(center=(BOUNDARIES[0] // 2, BOUNDARIES[1] // 2))

    screen.blit(text_surface, text_rect)

    pygame.display.flip()

def win_screen(screen):
    font = pygame.font.Font(None, 150)

    text_surface = font.render("Player win", True, (0, 255, 0))

    text_rect = text_surface.get_rect(center=(BOUNDARIES[0] // 2, BOUNDARIES[1] // 2))

    screen.blit(text_surface, text_rect)

    pygame.display.flip()


def game_loop():
    clock = pygame.time.Clock()
    running = True
    shooting = False

    fog_surface = pygame.Surface(BOUNDARIES, pygame.SRCALPHA)

    bullets = []

    obstacles = Utility.generate_obstacles(BOUNDARIES)

    enemies = Utility.generate_enemies(obstacles, BOUNDARIES)

    player = Player.Player(pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                shooting = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                shooting = False

        screen.fill(BACKGROUND_COLOR)

        if player.is_dead():
            screen.fill((0, 0, 0))
            lose_screen(screen)
            continue
        
        elif len(enemies) == 0:
            screen.fill((0, 0, 0))
            win_screen(screen)
            continue

        for obstacle in obstacles:
            obstacle.draw(screen)

        for bullet in bullets:
            bullet.draw(screen)


        player.handle_input()

        player.move()

        player.check_collision(obstacles)

        player.check_bounds([SCREEN_WIDTH, SCREEN_HEIGHT])

        player.update_angle()

        

        if shooting:
            player.shoot(bullets)

        for bullet in bullets:
            bullet.move()

            if bullet.check_collision(enemies, obstacles, BOUNDARIES, player):
                bullets.remove(bullet)
                enemies = sorted(enemies, key=lambda x: x == x.leader)

        for zombie in enemies:
            if zombie.leader == None:
                nearby_zombies = [z for z in enemies if z != zombie and z.leader == None and z.position.distance_to(zombie.position) < 100]
                if nearby_zombies:
                    zombie.set_leader(zombie)
                    for z in nearby_zombies:
                        z.set_leader(zombie)

        zombie_leaders = list(filter(lambda x: x.leader == x, enemies))
        enemies = sorted(enemies, key=lambda x: x == x.leader)

        for leader in zombie_leaders:
            for o_leader in zombie_leaders:
                if leader != o_leader:
                    distance = leader.position.distance_to(o_leader.position)
                    if distance < 100:
                        o_leader_followers = list(filter(lambda x: x.leader == o_leader, enemies))
                        for member in o_leader_followers:
                            member.set_leader(leader)

        for leader in zombie_leaders:
            if len(list(filter(lambda x: x.leader == leader, enemies))) > 5:
                leader.set_hunt_state()

        for zombie in enemies:
            zombie.move(obstacles, player, BOUNDARIES)
            zombie.draw(screen)

        for zombie in enemies:
            for o_zombie in enemies:
                zombie.clamp_zombie_positions(o_zombie)
            if Utility.circles_collide(zombie.position, Zombie.ENEMY_RADIUS, player.position, Player.PLAYER_SIZE):
                player.health -= 1

        fog_surface.fill(FOG_COLOR)

        player.draw_vision(fog_surface, obstacles, BOUNDARIES)

        screen.blit(fog_surface, (0, 0))

        player.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
