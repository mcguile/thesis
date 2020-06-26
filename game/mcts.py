import time
import math
import random


def random_policy(state):
    while not state.is_terminal():
        try:
            action = random.choice(state.get_possible_actions())
        except IndexError:
            raise Exception('No possible actions for non-terminal state ' + str(state))
        state = state.take_action(action)
    return state.get_reward()


class Node:
    def __init__(self, state, parent):
        self.state = state
        self.is_terminal = state.is_terminal()
        self.is_fully_expanded = self.is_terminal
        self.parent = parent
        self.num_visits = 0
        self.total_reward = 0
        self.children = {}


class MCTS:
    def __init__(self, time_limit=None, iter_limit=None, exploration_const=math.sqrt(2), rollout_policy=random_policy):
        self.root = None
        self.time_limit = time_limit
        self.iter_limit = iter_limit
        self.exploration_const = exploration_const
        self.rollout_policy = rollout_policy
        if time_limit and iter_limit:
            raise ValueError('Cannot have time limit and iteration limit. Choose one.')
        elif not time_limit and not iter_limit:
            raise ValueError('Must have one kind of limit - time or iteration.')
        elif iter_limit and iter_limit < 1:
            raise ValueError('Iteration limit must be greater than one.')

    def search(self, init_state):
        self.root = Node(init_state, None)
        if self.time_limit:
            time_limit = time.time() + self.time_limit/1000
            while time.time() < time_limit:
                self.execute_round()
        else:
            for _ in range(self.iter_limit):
                self.execute_round()
        best_child = self.get_best_child(self.root)
        return self.get_action(self.root, best_child)

    def execute_round(self):
        node = self.select_node(self.root)
        reward = self.rollout_policy(node.state)
        self.backprop(node, reward)

    def select_node(self, node):
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.get_best_child(node)
            else:
                return self.expand(node)
        return node

    def expand(self, node):
        actions = node.state.get_possible_actions()
        for action in actions:
            if action not in node.children:
                new_node = Node(node.state.take_action(action), node)
                node.children[action] = new_node
                if len(actions) == len(node.children):
                    node.is_fully_expanded = True
                return new_node
        raise Exception("Unreachable code reached")

    def backprop(self, node, reward):
        while node is not None:
            node.num_visits += 1
            node.total_reward += reward
            node = node.parent

    def get_best_child(self, node):
        best_val = float('-inf')
        best_nodes = []
        for child in node.children.values():
            node_val = node.state.get_current_player() * child.total_reward / child.num_visits + \
                       self.exploration_const * math.sqrt(math.log(node.num_visits) / child.num_visits)
            if node_val > best_val:
                best_val = node_val
                best_nodes = [child]
            elif node_val == best_val:
                best_nodes.append(child)
        return random.choice(best_nodes)

    def get_action(self, root, best_child):
        for action, node in root.children.items():
            if node is best_child:
                return action
