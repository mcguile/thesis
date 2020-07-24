import time
import math
import ray
import numpy as np
import timeout_decorator
import multiprocessing


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
    def __init__(self, time_limit=None, iter_limit=None, exploration_const=math.sqrt(2)):
        self.time_limit = time_limit
        self.iter_limit = iter_limit
        self.exploration_const = exploration_const
        self.best_val = float('-inf')
        self.rollout_policy = self.random_policy
        if time_limit and iter_limit:
            raise ValueError('Cannot have time limit and iteration limit. Choose one.')
        elif not time_limit and not iter_limit:
            raise ValueError('Must have one kind of limit - time or iteration.')
        elif iter_limit and iter_limit < 1:
            raise ValueError('Iteration limit must be greater than one.')

    @ray.remote
    def search(self, init_state):
        root = Node(init_state, None)
        if self.time_limit:
            time_limit = time.time() + self.time_limit/1000
            while time.time() < time_limit:
                self.execute_round(root)
        else:
            for i in range(self.iter_limit):
                try:
                    self.execute_round(root)
                except TimeoutError:
                    # print("timed out")
                    pass

            # print(self.action_reward)
        return root
        # best_child = self.get_best_child(root)
        # return self.get_action(root, best_child)

    @timeout_decorator.timeout(10, timeout_exception=TimeoutError)
    def execute_round(self, root):
        node, starting_action = self.select_node(root)
        reward = self.rollout_policy(node.state, starting_action)
        self.backprop(node, reward)

    def select_node(self, node):
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.get_best_child(node)
            else:
                return self.expand(node)
        return node, None

    def expand(self, node):
        actions = node.state.get_possible_actions()
        for action in actions:
            if action not in node.children:
                new_node = Node(node.state.take_action(action), node)
                node.children[action] = new_node
                if len(actions) == len(node.children):
                    node.is_fully_expanded = True
                return new_node, action
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
            if child.num_visits:
                node_val = node.state.players_turn * child.total_reward / child.num_visits + \
                           self.exploration_const * math.sqrt(math.log(node.num_visits) / child.num_visits)
                if node_val > best_val:
                    best_val = node_val
                    best_nodes = [child]
                elif node_val == best_val:
                    best_nodes.append(child)
        return np.random.choice(best_nodes)

    def get_action(self, root, best_child):
        for action, node in root.children.items():
            if node is best_child:
                # print(best_child.total_reward)
                return action

    def random_policy(self, state, starting_action):
        while not state.is_terminal():
            try:
                action = np.random.choice(state.get_possible_actions())
            except ValueError:
                time.sleep(1000000)
                raise Exception('No possible actions for non-terminal state ' + str(state))
            state = state.take_action(action)
        reward = state.get_reward()
        return reward

    def multiprocess_search(self, state):
        num_processes = multiprocessing.cpu_count()-1 or 1
        # p_t, p_p = (state.turn_count_white, "White") if state.players_turn == -1 else (state.turn_count_black, "Black")
        # print(f'MCTS - Executing {num_processes} parallel processes for {p_p} turn {p_t+1}')
        results = ray.get([self.search.remote(self, state) for _ in range(num_processes)])
        root = results[0]
        for node in results[1:]:
            for action, child in node.children.items():
                root.children[action].total_reward += child.total_reward
                root.children[action].num_visits += child.num_visits
        best_child = self.get_best_child(root)
        return self.get_action(root, best_child)
