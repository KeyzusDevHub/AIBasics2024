
import pygame
import random

WANDER_RADIUS = 100
WANDER_DISTANCE = 200
WANDER_JITTER = 5
MIN_DETECTION = 50
FEELER_RANGE = 30

class SteeringBehaviors:

    def __init__(self, enemy):
        self.steer_target = enemy
        self.wander_target = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
    
    # Przekazanie listy zombie do klasy
    def set_zombie_list(self, zombies):
        self.zombie_list = zombies

    # Chec podazania do punktu
    def Seek(self, target):
        des_vel = (target - self.steer_target.position).normalize()
        return des_vel

    # Chec podazania za graczem z predykcja jego przyszlego polozenia
    def Pursuit(self, player):
        if player.velocity != pygame.Vector2(0, 0) and abs(self.steer_target.velocity.angle_to(player.velocity)) > 20:
            future_time = self.steer_target.position.distance_to(player.position) / (ENEMY_SPEED * PLAYER_SPEED)
            return self.Seek(player.position + player.velocity * future_time)
        
        return self.Seek(player.position)
    
    # Ucieczka od danej pozycji w przeciwnym kierunku
    def Flee(self, target):
        des_vel = (self.steer_target.position - target).normalize()
        return des_vel

    # Ucieczka od danej pozycji z predykcja przyszlego polozenia
    def Evade(self, player):
        dist = player.position.distence_to(self.steer_target.position)
        future_time = dist / (ENEMY_SPEED * PLAYER_SPEED)
        return self.Flee(player.position * player.velocity * future_time)

    # Metoda swobodnego chodzenia po mapie
    def Wander(self):
        self.wander_target += pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * WANDER_JITTER
        self.wander_target.normalize_ip()

        self.wander_target *= WANDER_RADIUS
        w_t = self.wander_target + self.steer_target.velocity.normalize() * WANDER_DISTANCE

        return self.Seek(self.steer_target.position + w_t)
    
    # Metoda unikania przeszkod
    def ObstacleAvoidance(self, obstacles):
        # 1. Ustalenie przeszkod i punktow z nimi zwiazanych w okreslonym promieniu widzenia
        detection_len = MIN_DETECTION + (self.steer_target.velocity.length() / ENEMY_SPEED) * MIN_DETECTION
        detection_vec = self.steer_target.velocity.normalize() * detection_len
        intersections = self.ObstaclesWithinRange(obstacles, detection_vec)
        # 2. Gdy znaleziono choc jeden punkt na jego podstawie wyliczana jest sila
        if len(intersections) != 0:
            # 3. Wybierany jest punkt i przeszkoda najblizej gracza
            intersections = sorted(intersections, key=lambda x: x[0].distance_to(self.steer_target.position))
            i_obstacle = intersections[0][1]

            # 4. Szukanie punktu na przecieciu predkosci i wektora prostopadlego do niej
            p1_pos = self.steer_target.position
            p2_pos = i_obstacle.position
            direct = self.steer_target.velocity
            perp = pygame.Vector2(-direct.y, direct.x)

            point = self.do_rays_intersect(p1_pos, direct, p2_pos, perp)

            if point == None:
                perp = pygame.Vector2(direct.y, -direct.x)
                point = self.do_rays_intersect(p1_pos, direct, p2_pos, perp)
            
            # 5. Wyliczanie sil hamujacej i odpychajacej od przeszkody na bazie znalezionego punktu
            p_z_dist = (p1_pos - point).length()
            
            mult = 1.0 + (detection_len - p_z_dist) / detection_len
            brake_w = 0.2

            brake_f = -direct * brake_w

            lateral_f = mult * perp

            steering_f = brake_f + lateral_f

            if steering_f != pygame.Vector2(0, 0):
                self.wander_target = self.steer_target.velocity.normalize()

            return steering_f.normalize()

        return pygame.Vector2(0, 0)

    # Metoda szukajaca wszystkich przeszkod w danym zakresie widzenia
    def ObstaclesWithinRange(self, obstacles, det_r):
        intersetion_points = []
        for obstacle in obstacles:
            bigger_obstacle_tmp = Obstacle(obstacle.position, obstacle.radius + 0.5 * ENEMY_RADIUS)
            collision = Utility.ray_circle_intersection(self.steer_target.position, self.steer_target.position + det_r, bigger_obstacle_tmp)
            if collision != None:
                intersetion_points.append((collision, obstacle))
                collision2 = Utility.ray_circle_intersection(self.steer_target.position + det_r, self.steer_target.position, bigger_obstacle_tmp)
                if collision != collision2:
                    intersetion_points.append((collision2, obstacle))
        return intersetion_points
    
    # Metoda zwracajaca sile odpychajaca od brzegow mapy
    def WallAvoidance(self, bounds):
        feeler_dist = pygame.Vector2(FEELER_RANGE, FEELER_RANGE)
        feeler_point = self.steer_target.position + feeler_dist
        feeler_point2 = self.steer_target.position - feeler_dist
        steer_f = pygame.Vector2(0, 0)

        if feeler_point.x > bounds[0]:
            steer_f.x = bounds[0] - feeler_point.x
        elif feeler_point2.x > bounds[0]:
            steer_f.x = bounds[0] - feeler_point2.x
        elif feeler_point.x < 0: 
            steer_f.x = -feeler_point.x
        elif feeler_point2.x < 0:
            steer_f.x = -feeler_point2.x
        
        if feeler_point.y > bounds[1]:
            steer_f.y = bounds[1] - feeler_point.y
        elif feeler_point2.y > bounds[1]:
            steer_f.y = bounds[1] - feeler_point2.y
        elif feeler_point.y < 0:
            steer_f.y = -feeler_point.y
        elif feeler_point2.y < 0:
            steer_f.y = -feeler_point2.y
        
        if steer_f != pygame.Vector2(0, 0):
            self.wander_target = self.steer_target.velocity.normalize()

        return steer_f

    # Metoda liczaca sile ciagnaca zombie do siebie - grupujaca je
    def Cohesion(self):
        nearby_zombies = list(filter(lambda x: x.position.distance_to(self.steer_target.position) <= 300, self.zombie_list))
        if len(nearby_zombies) <= 1:
            return pygame.Vector2(0, 0)
        
        mass_center = pygame.Vector2(0, 0)
        for zombie in nearby_zombies:
            if zombie != self.steer_target:
                mass_center += zombie.position
        mass_center /= (len(nearby_zombies) - 1)

        if mass_center.distance_to(self.steer_target.position) > self.steer_target.radius:
            return self.Seek(mass_center) * mass_center.distance_to(self.steer_target.position) / 300
        else:
            return pygame.Vector2(0, 0)
        
    def Separation(self):
        nearby_zombies = list(filter(lambda x: x.position.distance_to(self.steer_target.position) <= 50, self.zombie_list))
        if len(nearby_zombies) <= 1:
            return pygame.Vector2(0, 0)
        
        force = pygame.Vector2(0, 0)
        for zombie in nearby_zombies:
            if zombie != self.steer_target:
                toAgent = (self.steer_target.position - zombie.position)
                force += toAgent.normalize() / toAgent.length()

        return force

    # Metoda wyliczajaca wspolny kierunek ruchu dla grupy zombie
    def Alignment(self):
        pos = self.steer_target.position
        is_any_memeber_aligned = list(filter(lambda x: x.position.distance_to(pos) < 150 and x.mode == "hunt" and x.alignment != None, self.zombie_list))
        if is_any_memeber_aligned:
            return is_any_memeber_aligned[0].alignment
        
        all_group_members = list(filter(lambda x: x.position.distance_to(self.steer_target.position) < 150 and x.mode == "hunt", self.zombie_list))
        directions_sum = pygame.Vector2(0, 0)
        for zombie in all_group_members:
            directions_sum += zombie.steering.Wander()

        return directions_sum.normalize() if directions_sum != pygame.Vector2(0, 0) else pygame.Vector2(0, 0)

    # Metoda zwracajaca odpowiednia pozycje do ukrycia sie przed graczem
    def GetHidingPosition(self, obstacle, player):

        dist_away = obstacle.radius + ENEMY_RADIUS
        to_obstacle = (obstacle.position - player.position).normalize()

        return (to_obstacle * dist_away) + obstacle.position

    # Metoda zwracajaca sile ciagnaca do punktu za polem widzenia gracza
    def Hide(self, obstacles, player):
        if (len(obstacles) == 0):
            return self.Evade(player)
        
        dist_based_obstacles = sorted(obstacles, key=lambda x: x.position.distance_to(self.steer_target.position))
        closest_obst = dist_based_obstacles[0]

        return self.Seek(self.GetHidingPosition(closest_obst, player))

    # Metoda sprawdzajaca czy dwa promienie przecinaja sie i zwracajaca punkt przeciecia
    def do_rays_intersect(self, P1, D1, P2, D2):
        p1_to_p2 = P2 - P1

        det = D1.x * D2.y - D1.y * D2.x

        t1 = (p1_to_p2.x * D2.y - p1_to_p2.y * D2.x) / det
        t2 = (p1_to_p2.x * D1.y - p1_to_p2.y * D1.x) / det

        if t1 >= 0 and t2 >= 0:
            return P1 + t1 * D1

        return None



from Zombie import ENEMY_SPEED, ENEMY_RADIUS
from Player import PLAYER_SPEED
from Obstacle import Obstacle
import Utility