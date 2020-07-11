from utils import distance_between_hex_cells, transform_cell_pos_from_velocity
import random
import numpy as np

w = 0.5
c1 = 0.8
c2 = 0.9


class Particle:
    def __init__(self, pos):
        self.pos = np.array(list(pos), dtype=int)
        self.pbest_pos = self.pos
        self.pbest_value = float('inf')
        self.vel = np.array([0, 0])

    def __str__(self):
        print(self.pos, " - my best is ", self.pbest_pos)

    def move(self):
        # TODO convert self.vel to new self.vel based on direction and column
        self.pos += self.vel


def convert_vel_beetle(vel):
    if vel > 0.25:
        return 1
    if vel < -0.25:
        return -1
    return 0


class Space:
    def __init__(self, state):
        self.state = state
        self.target = self.state.bee_pos_black
        self.particles = [Particle(pos) for pos in self.state.white_positions]
        self.gbest_value = float('inf')
        self.gbest_pos = [0, 0]

    def print_particles(self):
        for particle in self.particles:
            particle.__str__()

    def fitness(self, particle):
        return distance_between_hex_cells(particle.pos, self.target)

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
            new_vel = (w * particle.vel) + (c1 * random.random()) * (particle.pbest_pos - particle.pos) + \
                           (random.random() * c2) * (self.gbest_pos - particle.pos)
            print("position ", particle.pos, "new velocity ", new_vel)
            new_vel[0] = convert_vel_beetle(new_vel[0])
            new_vel[1] = convert_vel_beetle(new_vel[1])
            new_vel = new_vel.astype(int)
            yield particle, (from_r, from_c), new_vel, transform_cell_pos_from_velocity(new_vel, particle.pos)