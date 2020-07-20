from utils import distance_between_
import numpy as np
from insects import *
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
    def __init__(self, pos, insect_type):
        self.pos = np.array(list(pos), dtype=int)
        self.insect_type = insect_type
        self.pbest_pos = self.pos
        self.pbest_value = float('inf')
        self.vel = np.array([0, 0])
        self.vicinity = []
        self.best_vicin_val = float('inf')
        self.best_vicin_pos = np.array([0, 0])
        self.intention = 0
        self.desired_pos_nearest = None

    def __str__(self):
        return f'{self.insect_type} {self.pos} {self.intention}'

    def __repr__(self):
        return f'{self.insect_type} {self.pos} {self.intention}'

    def move(self):
        self.pos += self.vel

    def set_vicin_best(self, target):
        for particle in self.vicinity:
            best_fitness_candidate = fitness(particle, target)
            if self.best_vicin_val > best_fitness_candidate:
                self.best_vicin_val = best_fitness_candidate
                self.best_vicin_pos = particle.pos


class Space:
    def __init__(self, state, vicinities=False, vicin_radius=2):
        self.state = state
        self.target = self.state.bee_pos_black
        self.particles = [Particle((r, c), type(state.board.board[r][c])) for (r, c) in self.state.white_positions]
        self.gbest_value = float('inf')
        self.gbest_pos = np.array([0, 0])
        self.vicinities = vicinities
        self.vicin_radius = vicin_radius

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
        for particle in self.particles:
            from_r, from_c = particle.pos
            gbest_pos = self.gbest_pos if not self.vicinities else particle.best_vicin_pos
            new_vel = (w * particle.vel) + (c1 * np.random.random()) * (particle.pbest_pos - particle.pos) + \
                           (np.random.random() * c2) * (gbest_pos - particle.pos)
            yield particle, (from_r, from_c), new_vel

    def get_best_in_vicinities(self):
        best_in_vicins = set()
        for particle in self.particles:
            best_intent_val = 0
            best_intent_particle = None
            for p_in_vicin in particle.vicinity:
                if (p_in_vicin.intention >= best_intent_val) and \
                        (p_in_vicin.desired_pos_nearest != (p_in_vicin.pos[0], p_in_vicin.pos[1])):
                    best_intent_val = p_in_vicin.intention
                    best_intent_particle = p_in_vicin
            best_in_vicins.add(best_intent_particle)
        return best_in_vicins

    def get_best_particle_equal_score(self, best_in_vicins):
        best_overall_particle = None
        best_list = []
        best_overall_value = 0
        for particle in best_in_vicins:
            if particle.intention > best_overall_value:
                best_overall_value = particle.intention
                best_list = [particle]
            elif particle.intention == best_overall_value:
                best_list.append(particle)
        if len(best_list) == 1:
            return best_list[0]
        else:
            for particle in best_list:
                if particle.insect_type is Ant:
                    particle.intention += 5
                elif particle.insect_type is Beetle:
                    particle.intention += 4
                elif particle.insect_type is Grasshopper:
                    particle.intention += 3
                elif particle.insect_type is Spider:
                    particle.intention += 2
            best_overall_value = 0
            for particle in best_list:
                if particle.intention > best_overall_value:
                    best_overall_value = particle.intention
                    best_overall_particle = particle
            return best_overall_particle
