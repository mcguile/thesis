from state import State
from game_logic import *
from mcts import MCTS
import random
import ray

ray.init()

player_random = 'RANDOM'
player_mcts = 'MCTS'
player_swarm = 'SWARM'


class Game:
    def __init__(self, time_limit, iter_limit):
        self.time_limit = time_limit
        self.iter_limit = iter_limit
        self.state = State()

    def make_first_move_each(self):
        random.shuffle(self.state.white_pieces_start)
        random.shuffle(self.state.black_pieces_start)
        row, col = self.state.white_pieces_start[-1]
        self.state.hexa_selected = self.state.start_tiles.board[row][col]
        make_move(state=self.state, to_row=8, to_col=8, fromm_board=self.state.start_tiles)
        row, col = self.state.black_pieces_start[-1]
        self.state.hexa_selected = self.state.start_tiles.board[row][col]
        make_move(state=self.state, to_row=9, to_col=8, fromm_board=self.state.start_tiles)
        self.state.first_move_white = False
        self.state.first_move_black = False

    def make_mcts_move(self, action):
        if action.r_f < 0:
            action.r_f = abs(action.r_f) - 1
            self.state.hexa_selected = self.state.start_tiles.board[action.r_f][action.c_f]
            make_move(self.state, action.r_t, action.c_t, self.state.start_tiles)
        else:
            self.state.hexa_selected = self.state.board.board[action.r_f][action.c_f]
            make_move(self.state, action.r_t, action.c_t, self.state.board)

    def play_full_game(self, player1, player2):
        self.make_first_move_each()
        if player1 == player_mcts or player2 == player_mcts:
            mcts_ = MCTS(time_limit=self.time_limit, iter_limit=self.iter_limit)
        while not isGameOver(self.state):
            if self.state.players_turn == -1:
                if player1 == player_random:
                    make_random_move_from_anywhere(self.state)
                elif player1 == player_mcts:
                    action = mcts_.multiprocess_search(self.state)
                    self.make_mcts_move(action)
                else:
                    pass
            elif self.state.players_turn == 1:
                if player2 == player_random:
                    make_random_move_from_anywhere(self.state)
                elif player2 == player_mcts:
                    action = mcts_.multiprocess_search(self.state)
                    self.make_mcts_move(action)
                else:
                    pass
        if has_won(self.state, -1):
            print(f"White wins after {self.state.turn_count_white} turns")
        else:
            print(f"Black wins after {self.state.turn_count_black} turns")


game = Game(time_limit=None, iter_limit=100)
game.play_full_game(player1=player_random, player2=player_mcts)
