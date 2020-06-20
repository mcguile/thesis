from board import Board
from action import Action
from game_logic import *
W = 'white'
B = 'black'


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

    def getCurrentPlayer(self):
        """MCTS - enforced signature"""
        return self.players_turn

    def getPossibleActions(self):
        """MCTS - enforced signature"""
        s = deepcopy(self)
        possible_moves = []
        for row in range(self.board.height):
            for col, hexa in enumerate(self.board.board[row]):
                if hexa.player == self.players_turn:
                    s.hexa_selected = hexa
                    for move in get_possible_moves_from_board(s):
                        possible_moves.append(
                            Action(player=self.players_turn, r_f=row, c_f=col, r_t=move[0], c_t=move[1]))
        print(self.players_turn)
        return possible_moves

    def takeAction(self, action):
        """MCTS - enforced signature"""
        newstate = deepcopy(self)
        newstate.board.board[action.r_t][action.c_t] = self.board.board[action.r_f][action.c_f]
        newstate.board.board[action.r_f][action.c_f] = Blank()
        newstate.players_turn = opp(self.players_turn)
        return newstate

    def isTerminal(self):
        """MCTS - enforced signature"""
        return isGameOver(self) or not player_able_to_move(self)

    def getReward(self):
        """MCTS - enforced signature"""
        return has_won(self)