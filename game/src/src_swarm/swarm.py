from utils import distance_between_, transform_cell_pos_from_velocity
import random
import numpy as np
import math

w = 0.5
c1 = 0.8
c2 = 0.9
v_threshold = 0.25


def fitness(particle, target):
    d = distance_between_(particle.pos, target)
    if d == 0:
        # Beetle on top of goal
        d = 1
    return d


class Particle:
    def __init__(self, pos, seed=1):
        np.random.seed(seed)
        self.pos = np.array(list(pos), dtype=int)
        self.pbest_pos = self.pos
        self.pbest_value = float('inf')
        self.vel = np.random.randint(low=-4, high=5, size=2)
        self.vicinity = []
        self.best_vicin_val = float('inf')
        self.best_vicin_pos = np.array([0, 0])

    def __str__(self):
        print(self.pos, " - my best is ", self.pbest_pos)

    def move(self):
        self.pos += self.vel

    def set_vicin_best(self, target):
        for particle in self.vicinity:
            best_fitness_candidate = fitness(particle, target)
            if self.best_vicin_val > best_fitness_candidate:
                self.best_vicin_val = best_fitness_candidate
                self.best_vicin_pos = particle.pos


class Space:
    def __init__(self, state, vicinities=False, vicin_radius=2, seed=1):
        self.state = state
        self.target = self.state.bee_pos_black
        self.particles = [Particle(pos, seed) for pos in self.state.white_positions]
        self.gbest_value = float('inf')
        self.gbest_pos = np.array([0, 0])
        self.vicinities = vicinities
        self.vicin_radius = vicin_radius
        self.seed = seed

    def set_pbest(self):
        for particle in self.particles:
            best_fitness_candidate = fitness(particle, self.target)
            if particle.pbest_value > best_fitness_candidate:
                particle.pbest_value = best_fitness_candidate
                particle.pbest_pos = particle.pos

    def set_gbest(self):
        if not self.vicinities:
            for particle in self.particles:
                best_fitness_candidate = fitness(particle, self.target)
                if self.gbest_value > best_fitness_candidate:
                    self.gbest_value = best_fitness_candidate
                    self.gbest_pos = particle.pos
        else:
            # Create N vicinities for N particles
            for p1 in self.particles:
                for p2 in self.particles:
                    if distance_between_(p1.pos, p2.pos) <= self.vicin_radius:
                        p1.vicinity.append(p2)
                p1.set_vicin_best(self.target)

    def get_velocities(self):
        # print()
        for particle in self.particles:
            from_r, from_c = particle.pos
            # print(particle.pos, particle.pbest_pos, particle.pos - particle.pbest_pos)
            gbest_pos = self.gbest_pos if not self.vicinities else particle.best_vicin_pos
            new_vel = (w * particle.vel) + (c1 * random.random()) * (particle.pbest_pos - particle.pos) + \
                           (random.random() * c2) * (gbest_pos - particle.pos)
            # print("position ", particle.pos, "new velocity ", new_vel)
            yield particle, (from_r, from_c), new_vel
