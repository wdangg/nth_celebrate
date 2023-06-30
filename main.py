import pygame
import math
import os
from random import randint, uniform, choice, randrange

vector = pygame.math.Vector2
gravity = vector(0, 0.3)
WIDTH, HEIGHT = 1000, 730


trail_colours = [(249, 199, 79), (249, 132, 74), (248, 150, 30), (243, 114, 44), (249, 65, 68)]
white = (255, 255, 255)
dynamic_offset = 1
static_offset = 5

pygame.init()


class Firework:
    def __init__(self):
        self.colour = (255, 255, 255)
        self.colours = (choice(((255, 21, 22), (253, 148, 21), (254, 246, 23), (249, 132, 74), (62, 232, 21),
                                (22, 160, 232), (150, 20, 230), (142, 134, 147), (255, 255, 255))), white, white)
        self.firework = Particle(randrange(100, WIDTH - 100, 150), HEIGHT, True, self.colour)
        self.exploded = False
        self.particles = []
        self.min_max_particles = vector(200, 400)  # Minimum and maximum lifespan of exploded fireworks
        self.explode_sound = pygame.mixer.Sound('./sounds/firework.wav')

    def update(self, win):
        # Update the state of the firework
        if not self.exploded:
            self.firework.apply_force(gravity)
            self.firework.move()
            for tf in self.firework.trails:
                tf.show(win)

            self.show(win)

            if self.firework.vel.y >= -2:
                self.exploded = True
                self.explode()
        else:
            # Update the state of exploded particles
            for particle in self.particles:
                particle.apply_force(vector(gravity.x + uniform(-1, 1) / 20,
                                            gravity.y / 2 + (randint(1, 8) / 100)))
                particle.move()
                for t in particle.trails:
                    t.show(win)
                particle.show(win)

    def explode(self):
        # Create particles when the firework explodes
        amount = randint(int(self.min_max_particles.x), int(self.min_max_particles.y))
        for _ in range(amount):
            self.particles.append(Particle(self.firework.pos.x, self.firework.pos.y, False, self.colours))
            pygame.mixer.Channel(0).play(self.explode_sound)

    def show(self, win):
        # Show the firework
        pygame.draw.circle(win, self.colour, (int(self.firework.pos.x), int(self.firework.pos.y)), self.firework.size)

    def remove(self):
        # Check if the exploded firework needs to be removed
        if self.exploded:
            for p in self.particles:
                if p.remove is True:
                    self.particles.remove(p)

            if len(self.particles) == 0:
                return True
            else:
                return False


class Particle:
    def __init__(self, x, y, firework, colour):
        self.firework = firework
        self.pos = vector(x, y)
        self.origin = vector(x, y)
        self.radius = 20
        self.remove = False
        self.explosion_radius = randrange(15, 30, 5)
        self.life = 0
        self.acc = vector(0, 0)
        self.trails = []
        self.prev_posx = [-10] * 10
        self.prev_posy = [-10] * 10

        if self.firework:
            self.vel = vector(0, -randint(15, 20))  # Adjust the range here to change the velocity
            self.size = 4
            self.colour = colour
            for i in range(5):
                self.trails.append(Trail(i, self.size, True))
                pygame.mixer.Channel(1).play(pygame.mixer.Sound('./sounds/liftoff.wav'))
        else:
            self.vel = vector(uniform(-1, 1), uniform(-1, 1))
            self.vel.x *= 30
            self.vel.y *= 30
            self.size = randint(1, 3)
            self.colour = choice(colour)
            for i in range(5):
                self.trails.append(Trail(i, self.size, False))

    def apply_force(self, force):
        # Apply force to the particle
        self.acc += force

    def move(self):
        # Move the particle
        if not self.firework:
            self.vel.x *= 0.8
            self.vel.y *= 0.8

        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

        if self.life == 0 and not self.firework:
            distance = math.sqrt((self.pos.x - self.origin.x) ** 2 + (self.pos.y - self.origin.y) ** 2)
            if distance > self.explosion_radius:
                self.remove = True

        self.decay()

        self.trail_update()

        self.life += 1

    def show(self, win):
        # Show the particle
        pygame.draw.circle(win, (self.colour[0], self.colour[1], self.colour[2], 0),
                           (int(self.pos.x), int(self.pos.y)), self.size)

    def decay(self):
        # Decay the particle based on its lifespan
        if 100 > self.life > 20:  # Lifespan of the particle
            ran = randint(0, 30)
            if ran == 0:
                self.remove = True
        elif self.life > 100:  # Lifespan of the particle
            ran = randint(0, 5)
            if ran == 0:
                self.remove = True

    def trail_update(self):
        # Update trail positions based on previous positions
        self.prev_posx.pop()
        self.prev_posx.insert(0, int(self.pos.x))
        self.prev_posy.pop()
        self.prev_posy.insert(0, int(self.pos.y))

        for n, t in enumerate(self.trails):
            if t.dynamic:
                t.pos = vector(self.prev_posx[n + dynamic_offset], self.prev_posy[n + dynamic_offset])
            else:
                t.pos = vector(self.prev_posx[n + static_offset], self.prev_posy[n + static_offset])


class Trail:
    def __init__(self, n, size, dynamic):
        self.pos_in_line = n
        self.pos = vector(-10, -10)
        self.size = size
        self.dynamic = dynamic

    def show(self, win):
        # Show the trail
        pygame.draw.circle(win, (trail_colours[self.pos_in_line][0], trail_colours[self.pos_in_line][1],
                                 trail_colours[self.pos_in_line][2], 255 - self.pos_in_line * 50),
                           (int(self.pos.x), int(self.pos.y)), self.size)


def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("It's time to celebrate! Sweet birthdeyyy Nguyen Thuy Hanh dang iuuuuuuu!")
    clock = pygame.time.Clock()
    fireworks = []

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        win.fill((0, 0, 0))

        if randint(0, 8) == 0:
            fireworks.append(Firework())

        for firework in fireworks:
            firework.update(win)
            if firework.remove():
                fireworks.remove(firework)

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()

