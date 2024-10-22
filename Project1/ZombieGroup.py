


#Klasa określająca grupę zombie
class ZombieGroup:
    def __init__(self, leader, members=None):
        self.leader = leader 
        self.members = members if members else []
        self.hunting_player = False

    def add_member(self, zombie):
        if zombie != self.leader:
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
            #self.hunting_player = True
            pass

    def new_leader(self):
        if len(self.members) > 0:
            self.leader = self.members[0]
            self.members.remove(self.leader)
        else:
            self.leader = None

    def move(self, obstacles, player):

        self.check_group_size()

        if self.hunting_player:
            self.leader.chase_player(player)
        else:
            self.leader.move(obstacles, player)

        for member in self.members:
            member.follow_leader(self.leader)

        for member1 in self.members:
            for member2 in self.members:
                if member1 != member2 and not (member1 == self.leader or member2 == self.leader):
                    self.clamp_members_positions(member1, member2)

    def clamp_members_positions(self, member1, member2):
        dx = member1.x - member2.x
        dy = member1.y - member2.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < member1.radius + member2.radius:
            overlap = (member1.radius + member2.radius) - distance

            angle = math.atan2(dy, dx)

            member1.x += math.cos(angle) * overlap / 2
            member1.y += math.sin(angle) * overlap / 2
            member2.x -= math.cos(angle) * overlap / 2
            member2.y -= math.sin(angle) * overlap / 2
        
    def draw(self, screen):
        self.leader.draw(screen, (255, 255, 0))

        for member in self.members:
            member.draw(screen)

