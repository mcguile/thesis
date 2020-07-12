from utils import distance_between_, transform_cell_pos_from_velocity
import random
import numpy as np
import math

w = 0.5
c1 = 0.8
c2 = 0.9
v_threshold = 0.25


class Particle:
    def __init__(self, pos):
        self.pos = np.array(list(pos), dtype=int)
        self.pbest_pos = self.pos
        self.pbest_value = float('inf')
        self.vel = np.array([0, 0])

    def __str__(self):
        print(self.pos, " - my best is ", self.pbest_pos)

    def move(self):
        self.pos += self.vel


class Space:
    def __init__(self, state):
        self.state = state
        self.target = self.state.bee_pos_black
        self.particles = [Particle(pos) for pos in self.state.white_positions]
        self.gbest_value = float('inf')
        self.gbest_pos = np.array([0, 0])

    def print_particles(self):
        for particle in self.particles:
            particle.__str__()

    def fitness(self, particle):
        return distance_between_(particle.pos, self.target) - 1

    def set_pbest(self):
        for particle in self.particles:
            best_fitness_candidate = self.fitness(particle)
            if particle.pbest_value > best_fitness_candidate:
                particle.pbest_value = best_fitness_candidate
                particle.pbest_pos = particle.pos

    def set_gbest(self):
        for particle in self.particles:
            best_fitness_candidate = self.fitness(particle)
            if self.gbest_value > best_fitness_candidate:
                self.gbest_value = best_fitness_candidate
                self.gbest_pos = particle.pos

    def move_particles(self):
        print()
        for particle in self.particles:
            from_r, from_c = particle.pos
            print(particle.pos, particle.pbest_pos, particle.pos - particle.pbest_pos)
            new_vel = (w * particle.vel) + (c1 * random.random()) * (particle.pbest_pos - particle.pos) + \
                           (random.random() * c2) * (self.gbest_pos - particle.pos)
            print("position ", particle.pos, "new velocity ", new_vel)
            yield particle, (from_r, from_c), new_vel
