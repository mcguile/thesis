import os
from game import *
from mcts import MCTS
from swarm import Space
import logging

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

player_random = 'RANDOM'
player_mcts = 'MCTS'
player_swarm = 'SWARM'


class GameNoUI:
    def __init__(self, state, player1, player2, vicinities=False, vicin_radius=3,
                 generate_full_board=False,
                 random_moves_after_generate=0,
                 intention_criteria=4, full_swarm_move=False, infinite_moves=False,
                 log_file=None):
        self.state = state
        self.mcts = MCTS(time_limit=self.state.time_limit, iter_limit=self.state.iter_limit)
        self.vicinities = vicinities
        self.vicin_radius = vicin_radius
        self.space = None if generate_full_board else Space(self.state, self.vicinities, self.vicin_radius)
        self.player1 = player1
        self.player2 = player2
        self.generate = generate_full_board
        self.rand_moves = random_moves_after_generate
        self.intention_criteria = intention_criteria
        self.full_swarm_move = full_swarm_move
        self.inf_moves = infinite_moves
        if log_file:
            for handler in logging.root.handlers[:]:
                handler.close()
                logging.root.removeHandler(handler)
            logging.basicConfig(filename=log_file, level=logging.INFO, format='%(message)s')

    def play_full_game(self):
        if self.generate:
            logging.info(generate_random_full_board(self.state))
            if self.rand_moves:
                while self.state.turn_count_white < self.rand_moves + 11:
                    try:
                        move = make_random_move_from_board(self.state)
                        if move:
                            logging.info(move)
                    except IndexError:
                        self.state.players_turn = opp(self.state.players_turn)
        else:
            logging.info(make_first_move_each(self.state))
        logging.info('ai')
        white_space = Space(self.state, player=W, vicinities=self.vicinities, vicin_radius=self.vicin_radius)
        black_space = Space(self.state, player=B, vicinities=self.vicinities, vicin_radius=self.vicin_radius)
        while not isGameOver(self.state) and self.state.turn_count_white < (11 + self.rand_moves + 40):
            self.space = white_space if self.state.players_turn == W else black_space
            if self.state.players_turn == W:
                if self.player1 == player_random:
                    logging.info(make_random_move_from_anywhere(self.state))
                elif self.player1 == player_mcts:
                    action = self.mcts.multiprocess_search(self.state)
                    logging.info(make_mcts_move(self.state, action))
                else:
                    logging.info(make_swarm_move(self.state, self.space, self.intention_criteria, self.full_swarm_move, self.inf_moves))
            elif self.state.players_turn == B:
                if self.player2 == player_random:
                    logging.info(make_random_move_from_anywhere(self.state))
                elif self.player2 == player_mcts:
                    action = self.mcts.multiprocess_search(self.state)
                    logging.info(make_mcts_move(self.state, action))
                else:
                    logging.info(make_swarm_move(self.state, self.space, self.intention_criteria, self.full_swarm_move, self.inf_moves))
        hww = has_won(self.state, W)
        hwb = has_won(self.state, B)
        if hww:
            # print(f"White wins after {self.state.turn_count_white} turns")
            return -1
        elif hwb:
            # print(f"Black wins after {self.state.turn_count_black} turns")
            return 1
        return 0
