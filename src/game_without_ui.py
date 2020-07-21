from game import *
from mcts import MCTS
from swarm import Space
import ray

ray.init()

player_random = 'RANDOM'
player_mcts = 'MCTS'
player_swarm = 'SWARM'


class GameNoUI:
    def __init__(self, state, player1, player2, vicinities=False, vicin_radius=3,
                 generate_full_board=False,
                 random_moves_after_generate=0,
                 intention_criteria=4, full_swarm_move=False):
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

    def play_full_game(self):
        if self.generate:
            generate_random_full_board(self.state)
            self.space = Space(self.state, self.vicinities, self.vicin_radius)
            if self.rand_moves:
                while self.state.turn_count_white < self.rand_moves + 11:
                    try:
                        make_random_move_from_board(self.state)
                    except IndexError:
                        self.state.players_turn = opp(self.state.players_turn)

            # self.state.players_turn = -1
        else:
            make_first_move_each(self.state)
        while not isGameOver(self.state) and self.state.turn_count_white < (11 + self.rand_moves + 100):
            if self.state.players_turn == -1:
                if self.player1 == player_random:
                    make_random_move_from_anywhere(self.state)
                elif self.player1 == player_mcts:
                    action = self.mcts.multiprocess_search(self.state)
                    make_mcts_move(self.state, action)
                else:
                    make_swarm_move(self.state, self.space, self.intention_criteria, self.full_swarm_move)
            elif self.state.players_turn == 1:
                if self.player2 == player_random:
                    make_random_move_from_anywhere(self.state)
                elif self.player2 == player_mcts:
                    action = self.mcts.multiprocess_search(self.state)
                    print("Black", action)
                    make_mcts_move(self.state, action)
                else:
                    make_swarm_move(self.state, self.space, self.intention_criteria, self.full_swarm_move)
        hww = has_won(self.state, -1)
        hwb = has_won(self.state, 1)
        if hww:
            # print(f"White wins after {self.state.turn_count_white} turns")
            return -1
        elif hwb:
            # print(f"Black wins after {self.state.turn_count_black} turns")
            return 1
        return 0
