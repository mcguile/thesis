from board import Board
from action import Action
from game_logic import *
W = -1
B = 1


class State:
    def __init__(self, board=None, start_tiles=None):
        self.depth_limit = 10
        self.board = board if board else Board(16, 16)
        self.start_tiles = start_tiles if start_tiles else Board(6, 5, True)
        self.players_turn = W
        self.hexa_selected = None
        self.hexa_selected_is_on_board = False
        self.bee_placed_white, self.bee_placed_black = False, False
        self.bee_pos_white, self.bee_pos_black = (0, 3), (3, 3)
        self.turn_count_white, self.turn_count_black = 0, 0
        self.plies_checked = 0
        self.possible_moves = set()
        self.prev_state = None

    def get_current_player(self):
        return self.players_turn

    def get_possible_actions(self):
        possible_moves = []
        # BOARD
        for row in range(self.board.height):
            for col, hexa in enumerate(self.board.board[row]):
                if hexa.player == self.players_turn:
                    self.hexa_selected = hexa
                    for move in get_possible_moves_from_board(self):
                        possible_moves.append(
                            Action(player=self.players_turn, r_f=row, c_f=col, r_t=move[0], c_t=move[1]))
        # RACK
        # disabled due to huge increase in time for decision making
        # start, stop = get_rack_inidices(s.players_turn)
        # got_targets = False
        # targets = []
        # insect_types = [Ant, Beetle, Grasshopper, Bee, Spider]
        # move_found_insect_type = [False]*len(insect_types)
        # for row in range(start, stop):
        #     for col, hexa in enumerate(s.start_tiles.board[row]):
        #         if type(hexa) is not Blank:
        #             s.hexa_selected = hexa
        #             if not got_targets:
        #                 for move in get_possible_moves_from_rack(s):
        #                     targets.append(move)
        #                 got_targets = True
        #             if type(hexa) == insect_types[col] and not move_found_insect_type[col]:
        #                 # Optimisation - only consider one set of moves for each insect type
        #                 move_found_insect_type[col] = True
        #                 for move in targets:
        #                     possible_moves.append(
        #                         Action(player=s.players_turn, r_f=-row - 1, c_f=col, r_t=move[0], c_t=move[1]))
        return possible_moves

    def take_action(self, action):
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
