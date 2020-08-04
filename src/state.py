from board import Board
from action import Action
from game import *
from copy import deepcopy

W = -1
B = 1


class State:
    def __init__(self, board=None, start_tiles=None, time_limit=None, iter_limit=100):
        self.depth_limit = 13
        self.time_limit = time_limit
        self.iter_limit = iter_limit
        self.board = board if board else Board(16, 16)
        self.start_tiles = start_tiles if start_tiles else Board(6, 5, True)
        self.players_turn = W
        self.hexa_selected = None
        self.hexa_selected_is_on_board = False
        self.bee_placed_white, self.bee_placed_black = False, False
        self.bee_pos_white, self.bee_pos_black = (0, 3), (3, 3)
        self.turn_count_white, self.turn_count_black = 0, 0
        self.white_pieces_start = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2), (1, 2), (2, 2), (0, 3), (0, 4), (1, 4)]
        self.black_pieces_start = [(3, 0), (4, 0), (5, 0), (3, 1), (4, 1), (3, 2), (4, 2), (5, 2), (3, 3), (3, 4), (4, 4)]
        self.first_move_white = True
        self.first_move_black = True
        self.plies_checked = 0
        self.white_positions = set()
        self.black_positions = set()
        self.possible_moves = set()
        self.insect_types = [Ant, Beetle, Grasshopper, Bee, Spider]
        self.prev_state = None

    def get_possible_actions(self):
        possible_moves = []
        # BOARD
        positions = self.black_positions if self.players_turn == B else self.white_positions
        for r, c in positions:
            self.hexa_selected = self.board.board[r][c]
            for r_t, c_t in get_possible_moves_from_board(self):
                possible_moves.append(
                    Action(player=self.players_turn, r_f=r, c_f=c, r_t=r_t, c_t=c_t))
        # RACK
        # if self.players_turn == W and not self.bee_placed_white and self.turn_count_white == 3:
        #     self.hexa_selected = self.start_tiles.board[0][3]
        #     moves = get_possible_moves_from_rack(self)
        #     for move in moves:
        #         possible_moves.append(Action(player=self.players_turn, r_f=-1, c_f=3, r_t=move[0], c_t=move[1]))
        # elif self.players_turn == B and not self.bee_placed_black and self.turn_count_black == 3:
        #     self.hexa_selected = self.start_tiles.board[3][3]
        #     moves = get_possible_moves_from_rack(self)
        #     for move in moves:
        #         possible_moves.append(Action(player=self.players_turn, r_f=-4, c_f=3, r_t=move[0], c_t=move[1]))
        # else:
        #     start, stop = get_rack_inidices(self.players_turn)
        #     got_targets = False
        #     targets = []
        #     move_found_insect_type = [False]*len(self.insect_types)
        #     for row in range(start, stop):
        #         for col, hexa in enumerate(self.start_tiles.board[row]):
        #             if type(hexa) is not Blank:
        #                 self.hexa_selected = hexa
        #                 if not got_targets:
        #                     for move in get_possible_moves_from_rack(self):
        #                         targets.append(move)
        #                     got_targets = True
        #                 if type(hexa) == self.insect_types[col] and not move_found_insect_type[col]:
        #                     # Optimisation - only consider one set of moves for each insect type
        #                     move_found_insect_type[col] = True
        #                     for move in targets:
        #                         possible_moves.append(
        #                             Action(player=self.players_turn, r_f=-row - 1, c_f=col, r_t=move[0], c_t=move[1]))
        # print(self.players_turn, ' POSSIBLE MOVES: ', possible_moves)
        return possible_moves

    def take_action(self, action):
        # print('TAKE ACTION: ', action)
        new_state = deepcopy(self)
        new_state.plies_checked += 1
        if action:
            if action.r_f < 0:
                #  We are moving from a rack
                new_state.hexa_selected = new_state.start_tiles.board[abs(action.r_f)-1][action.c_f]
                make_move(new_state, action.r_t, action.c_t, new_state.start_tiles)
            else:
                #  We are moving from the board
                new_state.hexa_selected = new_state.board.board[action.r_f][action.c_f]
                make_move(new_state, action.r_t, action.c_t, new_state.board)
        return new_state

    def depth_limit_reached(self):
        if self.depth_limit and self.plies_checked == self.depth_limit:
            self.plies_checked = 0
            return True
        return False

    def is_terminal(self):
        return isGameOver(self) or self.depth_limit_reached()

    def get_reward(self):
        return get_reward(self)
