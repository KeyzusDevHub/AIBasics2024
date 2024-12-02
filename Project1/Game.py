import pygame
import sys
import Utility
import Player
import Zombie

# Stałe rozmiary ekranu
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800

# Kolory
BACKGROUND_COLOR = (255, 255, 255)
VISION_COLOR = (0, 0, 0, 0)

# Brzegi ekranu
BOUNDARIES = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Inicjalizacja pygame
pygame.init()

# Utworzenie okna gry
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gra o strzelaniu przez trójkątnego gracza do okrągłych zombie z kolistymi przeszkodami, mgłą wojny i sztuczną inteligencją opartą o emergentne zachowania")

# Plansza po przegranej
def lose_screen(screen):
    font = pygame.font.Font(None, 150)

    text_surface = font.render("Zombie win", True, (255, 0, 0))

    text_rect = text_surface.get_rect(center=(BOUNDARIES[0] // 2, BOUNDARIES[1] // 2))

    screen.blit(text_surface, text_rect)

    pygame.display.flip()

# Plansza po wygranej
def win_screen(screen):
    font = pygame.font.Font(None, 150)

    text_surface = font.render("Player win", True, (0, 255, 0))

    text_rect = text_surface.get_rect(center=(BOUNDARIES[0] // 2, BOUNDARIES[1] // 2))

    screen.blit(text_surface, text_rect)

    pygame.display.flip()

# Petla gry
def game_loop():
    clock = pygame.time.Clock()
    running = True
    shooting = False

    fog_surface = pygame.Surface(BOUNDARIES, pygame.SRCALPHA)

    bullets = []

    obstacles = Utility.generate_obstacles(BOUNDARIES)

    enemies = Utility.generate_enemies(obstacles, BOUNDARIES)

    player = Player.Player(pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    for enemy in enemies:
        enemy.steering.set_zombie_list(enemies)

    while running:

        # Obsluga podstawowych zdarzen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                shooting = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                shooting = False

        screen.fill(BACKGROUND_COLOR)

        # Obsluga konca gry
        if player.is_dead():
            screen.fill((0, 0, 0))
            lose_screen(screen)
            continue
        
        elif len(enemies) == 0:
            screen.fill((0, 0, 0))
            win_screen(screen)
            continue

        # Rysowanie przeszkod i pociskow
        for obstacle in obstacles:
            obstacle.draw(screen)

        for bullet in bullets:
            bullet.draw(screen)

        # Blok obslugi gracza
        player.handle_input()
        player.move()
        player.check_collision(obstacles)
        player.check_bounds([SCREEN_WIDTH, SCREEN_HEIGHT])
        player.update_angle()

        if shooting:
            player.shoot(bullets)

        # Sprawdzenie kolizji pociskow
        for bullet in bullets:
            bullet.move()

            if bullet.check_collision(enemies, obstacles, BOUNDARIES):
                bullets.remove(bullet)

        # Szukanie pobliskich zombie do ataku
        for zombie in enemies:
            if zombie.mode != "hunt":
                nearby_zombies = [z for z in enemies if z.mode != "hunt" and z.position.distance_to(zombie.position) < 150]
                if len(nearby_zombies) >= 5:
                    for z in nearby_zombies:
                        z.set_hunt_state()

        # Ruch zombie
        for zombie in enemies:
            zombie.move(obstacles, player, BOUNDARIES, clock.get_fps() / 500)
            zombie.draw(screen)

        # Poprawa pozycji zombie i sprawdzenie czy trafily gracza
        for zombie in enemies:
            for o_zombie in enemies:
                zombie.clamp_zombie_positions(o_zombie)
            if Utility.circles_collide(zombie.position, Zombie.ENEMY_RADIUS, player.position, Player.PLAYER_SIZE):
                player.health -= 1

        # Rysowanie wizji planszy
        fog_surface.fill(VISION_COLOR)
        player.draw_vision(fog_surface, obstacles, BOUNDARIES)
        screen.blit(fog_surface, (0, 0))
        player.draw(screen)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
