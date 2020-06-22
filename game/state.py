from board import Board
from action import Action
from game_logic import *
W = -1
B = 1


class State:
    def __init__(self, board=None, start_tiles=None):
        self.board = board if board else Board(16, 16)
        self.start_tiles = start_tiles if start_tiles else Board(6, 5, True)
        self.players_turn = W
        self.hexa_selected = None
        self.hexa_selected_is_on_board = False
        self.bee_placed_white, self.bee_placed_black = False, False
        self.bee_pos_white, self.bee_pos_black = (0, 3), (3, 3)
        self.turn_count_white, self.turn_count_black = 0, 0
        self.possible_moves = set()
        self.prev_state = None

    def get_current_player(self):
        return self.players_turn

    def get_possible_actions(self):
        s = deepcopy(self)
        possible_moves = []
        # BOARD
        for row in range(s.board.height):
            for col, hexa in enumerate(s.board.board[row]):
                if hexa.player == s.players_turn:
                    s.hexa_selected = hexa
                    for move in get_possible_moves_from_board(s):
                        possible_moves.append(
                            Action(player=s.players_turn, r_f=row, c_f=col, r_t=move[0], c_t=move[1]))
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
        if not action:
            new_state.players_turn = opp(new_state.players_turn)
        else:
            if action.r_f < 0:
                #  We are moving from a rack
                new_state.board.board[action.r_t][action.c_t] = new_state.start_tiles.board[abs(action.r_f)-1][action.c_f]
            else:
                #  We are moving from the board
                new_state.board.board[action.r_t][action.c_t] = new_state.board.board[action.r_f][action.c_f]
            new_state.board.board[action.r_f][action.c_f] = Blank()
            new_state.players_turn = opp(new_state.players_turn)
        return new_state

    def is_terminal(self):
        return isGameOver(self)

    def get_reward(self):
        if has_won(self, W):
            return -1
        elif has_won(self, B):
            return 1
        return False
